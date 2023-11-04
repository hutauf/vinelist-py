"""vinelist-py
Usage: python3 main.py

vinelist-py is a script that scrapes the Amazon Vine website and retrieves all products that you have ordered.
Note that you must be logged in to Amazon for this to work.
It is strongly recommended to check if your chromedriver version matches your Chrome version.
"""
from selenium.webdriver import Chrome, ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import os
import argparse
import time


class Product:
    """
    Product class that represents a product ordered on Amazon Vine. It contains the title, link, order date and price of the product.
    The default price is €0.00, if the price is not available it will be left on €0.00.
    """

    def __init__(self, title, link, order_date, price="0,00€"):
        self.title = title
        self.link = link
        self.order_date = order_date
        self.price = price

    def __str__(self):
        return (
            "Title: "
            + self.title
            + "\nLink: "
            + self.link
            + "\nOrder date: "
            + self.order_date
            + "\nPrice: "
            + self.price
            + "\n"
        )

    def __repr__(self):
        return (
            "Title: "
            + self.title
            + "\nLink: "
            + self.link
            + "\nOrder date: "
            + self.order_date
            + "\nPrice: "
            + self.price
            + "\n"
        )

    def __eq__(self, other):
        return (
            self.title == other.title
            and self.link == other.link
            and self.order_date == other.order_date
            and self.price == other.price
        )

    def __hash__(self):
        return hash((self.title, self.link, self.order_date, self.price))

    def csv(self):
        # safely return the title, replace the comma with a dot without changing the original title of the object
        return (
            self.title.replace(";", ",")
            + ";"
            + self.link
            + ";"
            + self.order_date
            + ";"
            + self.price
        )


def main():
    """
    Main function that parses the command line arguments, sets up the Chrome driver and starts the scraping process.
    """
    args = setup()
    products = []
    BASE_URL = "https://www.amazon.de/-/en/vine/orders?page="
    START_PAGE = 1
    END_PAGE = int(args.pages)

    chrome_options = Options()
    if args.headless:
        chrome_options.add_argument("--headless")
    if not args.chromedriver_path:
        try:
            # use the chromedriver that is installed by chromedriver-py
            from chromedriver_py import binary_path

            chromedriver_path = binary_path or chromedriver_path
        except:
            log(
                "WARN",
                "Could not find installed chromedriver-py, trying provided chromedriver",
            )
            if not os.path.exists(chromedriver_path):
                log(
                    "ERROR",
                    "Could not find chromedriver at "
                    + chromedriver_path
                    + ", please provide the correct path to chromedriver with --chromedriver-path",
                )
                exit(1)

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    # use the cookiejar from the Chrome browser
    if args.chromeprofile:
        chrome_options.add_argument("--user-data-dir=" + args.chromeprofile)

    # set user agent to Chrome
    chrome_options.add_argument("--user-agent=" + get_user_agent())

    log(
        "INFO",
        "Starting the first instance of Chrome. Take some time to log in to Amazon!",
    )
    with Chrome(
        service=ChromeService(executable_path=chromedriver_path),
        options=chrome_options,
    ) as driver:
        driver.implicitly_wait(10)
        driver.get(BASE_URL + "1")
        time.sleep(30)

    for i in range(START_PAGE, END_PAGE + 1):
        with Chrome(
            service=ChromeService(executable_path=chromedriver_path),
            options=chrome_options,
        ) as driver:
            driver.implicitly_wait(5)
            driver.get(BASE_URL + str(i))
            log("INFO", "Page: " + str(i))
            orders = driver.find_elements(
                By.XPATH, "//tr[@class='vvp-orders-table--row']"
            )
            log("INFO", "Orders: " + str(len(orders)))
            for order in orders:
                try:
                    product_title = order.find_element(
                        By.XPATH, ".//td[@class='vvp-orders-table--text-col']/a"
                    )
                    product_title_text = product_title.find_element(
                        By.XPATH, ".//span[@class='a-truncate-full a-offscreen']"
                    ).get_attribute("innerHTML")
                    product_link = product_title.get_attribute("href")
                    order_date = order.find_element(
                        By.XPATH, ".//td[@data-order-timestamp]"
                    )
                    products.append(
                        Product(
                            product_title_text,
                            product_link,
                            format_date(order_date.get_attribute("innerHTML")),
                        )
                    )
                except:
                    log(
                        "WARN",
                        "Error while parsing order on page "
                        + str(i)
                        + " - review the page manually to see if the product is still available",
                    )
    log("INFO", "Successfully parsed " + str(len(products)) + " products")
    log("INFO", "Retrieving prices for products")
    with Chrome(
        service=ChromeService(executable_path=chromedriver_path), options=chrome_options
    ) as driver:
        driver.implicitly_wait(2)
        for product in products:
            log(
                "INFO",
                "Retrieving price for product "
                + str(products.index(product) + 1)
                + " out of "
                + str(len(products)),
            )
            # retrieve the price of the product from the product page
            driver.get(product.link)
            # wait until the price is loaded, its located inside a span with class="a-price aok-align-center reinventPricePriceToPayMargin priceToPay"
            try:
                price = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "//span[@class='a-price aok-align-center reinventPricePriceToPayMargin priceToPay']",
                        )
                    )
                )
                product.price = format_price(
                    price.find_element(
                        By.XPATH, ".//span[@class='a-offscreen']"
                    ).get_attribute("innerHTML")
                )
            except TimeoutException:
                log("WARN", "Did not find price for product: " + product.link)
                log(
                    "WARN",
                    "Review the product manually to see if it is still available. It is a known issue that articles offered in varying colors or sizes are not parsed correctly.",
                )
    log("INFO", "Successfully retrieved " + str(len(products)) + " products")
    log("INFO", "Writing products to vine.csv")
    # write the products to a CSV file
    with open("vine.csv", "w") as f:
        f.write("Title;Link;Order Date;Price\n")
        for product in products:
            f.write(product.csv() + "\n")

    log("INFO", "Successfully wrote " + str(len(products)) + " products to vine.csv")


def get_user_agent():
    """Returns a random user agent string from https://user-agents.net/random"""
    import requests, re

    res = requests.get("https://user-agents.net/random")
    return (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        if res.status_code != 200
        else "Mozilla" + re.search(r"Mozilla(.*)", res.text).group(1).split("<")[0]
    )


def format_date(date):
    """Incoming is mm/dd/yyyy, outgoing is dd.mm.yyyy (European format)
    month and day can be single digit, year is always 4 digits"""
    date_split = date.split("/")
    return date_split[1] + "." + date_split[0] + "." + date_split[2]


def format_price(price):
    """incoming is €x.xx, outgoing is x,xx€"""
    price_split = price.split("€")
    return price_split[1].replace(".", ",") + "€"


def log(level, message):
    """Logs a message with a given level to the console"""
    print("[" + level + "] " + message)


def setup():
    """Parses the command line arguments and returns them"""
    log("INFO", "Starting vinelist-py")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pages", help="Amount of Vine Order pages to scrape", required=True
    )
    parser.add_argument(
        "--chromeprofile", help="Chrome profile to reuse", required=False
    )
    parser.add_argument(
        "--headless",
        help="Run Chrome in headless mode",
        action="store_true",
        required=False,
    )
    parser.add_argument(
        "--chromedriver-path",
        help="Path to chromedriver executable",
        required=False,
    )
    return parser.parse_args()


if __name__ == "__main__":
    """Checks if the script is run directly and calls the main function"""
    main()
    log("INFO", "Finished vinelist-py")
