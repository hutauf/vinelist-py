
# vinelist-py

A small utility written in Python 3.10 to create CSV sheets which contain your Amazon Vine orders and **current** prices.

## Important Disclaimer

**This code is for demonstration and learning purposes only. Amazon expressly states in its general terms and conditions that it is not permitted to automatically access or evaluate Amazon content using scripts or robots. I would therefore like to expressly point out at this point that I do not encourage this and that the script is not intended for such purposes.**

## Acknowledgements

- [readme.so](https://readme.so) because they take the pain of out writing READMEs

## FAQ

### How does this work?

The script programmatically opens your Chrome browser (which you can log in to Amazon, if you're not already logged in) and looks through your orders page-for-page. It then takes the retrieved product URLs and uses them to retrieve current prices for you.

### I don't understand this stuff

This script is publicly available for everyone. If there are any techies out there who want to write an _easy_ and _understandable_ README, you're very welcome to do so and open a PR!

### It does not work for me

Please open a GitHub Issue and describe your problem.

## Usage/Examples

I wrote and tested this script with **Python 3.10** - my guess is that it is going to work with every Python 3.x version, but I can't tell for sure.

Also, I only ran this on Linux (Linux Mint 21.2) yet. IMHO it _should_ also work fine on Windows and MacOS if you install below stuff.

### Prerequisites

- The repository must be present on your local machine. If you do not know how to download it, visit [this tutorial](https://docs.github.com/en/repositories/working-with-files/using-files/downloading-source-code-archives).
- [Python](https://www.python.org/downloads/) in version 3.
- [pip](https://pip.pypa.io/en/stable/installation/). `pip` is a package manager for Python which allows you to install external libraries which I used inside the script.
  - `pip` dependencies - In this repository, I placed a `requirements.txt` which you can use like this: `pip install -r requirements.txt`.
- A [Google Chrome installation](https://www.google.com/chrome/). This will be used to visit Amazon via a legit browser.
  - Have a good look at the exact version you are using. Adjust the `requirements.txt` accordingly to your Chrome version, so the correct chrome-driver will be downloaded with pip. _Technically_, you can use your own chromedriver installation.

### Running

- Determine your local Chrome profile. If you can't find it, look at [this documentation](https://chromium.googlesource.com/chromium/src/+/master/docs/user_data_dir.md#Default-Location) which describes it. We are going to reuse your existing profile for convenience reasons, so you won't need to login to Amazon every time the browser opens.
- Determine the amount of Vine order pages you need to scrape. For testing purposes, you can start with `2` or `3` pages and see if you like the resulting CSV file.

To see all possible options, run:

```bash
python main.py -h
```

For example, if you are running Linux and already have a profile, run:

```bash
python main.py \
  --profile=/home/<your_username>/.config/google-chrome/Default \
  --pages=70
```

**NOTE**: When the script starts, it will open a Chrome window for you to login to Amazon. This login will be re-used then. If the window already shows you as logged in (i.e. you can see your Vine orders), you can simply wait until the rest of the script starts.

## Known Issues

The script was written in about 1 hour, so it currently has its limitations:

- Products which come in different sizes/colors may not show prices in the CSV file. This only happens on products which do not have a selected size/color when the product page is visited, so a price is not shown and can not be scraped.
- If you have many products to scan, the scan takes some time. Each order page takes about 1-2 seconds to scan in about 10 products, and each product page is going to need about 2-3 seconds.
- The prices shown are **current** prices. They do not match the price from the date you ordered the product. I repeat, **this script does _not_ retrieve historic prices right now.**

## Upcoming: Marking unavailable products

Work in progress, but you can already use it if you want to.

In some cases, the main script is not able to determine a current price because the product is listed as "Currently unavailable". In this case, the script will mark the product with  `0,00€` in the CSV file. You can then manually look up the product and enter the price yourself, or you can soon run `python unavailable.py` which will open a Chrome window and check all products with price `0,00€`, which are marked as unavailable when they're not listed anymore. You may then manually look up historic prices on camelcamelcamel or keepa and enter it in the CSV file.

## License

See [LICENSE](LICENSE). This project is licensed under the terms of the MIT license. In easy words, you can do whatever you want with this code, but you may not hold me liable for any damage caused by this code.
