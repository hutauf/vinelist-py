# -*- coding: utf-8 -*-
import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

input_file = "vine.csv"

# column headers: Title,Link,Order Date,Price

options = Options()
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)


with open(input_file, "r") as csvfile:
    num_lines = len(open(input_file).readlines())
    with open("vine_with_unavailable.csv", "w") as f:
        # f.write("Title;Link;Order Date;Price\n")
        reader = csv.DictReader(f=csvfile, delimiter=";")
        writer = csv.DictWriter(f, fieldnames=reader.fieldnames)
        writer.writeheader()
        for row in reader:
            if row["Price"] == "0,00€":
                url = row["Link"]
                driver.get(url)
                time.sleep(2)
                if "Currently unavailable" in driver.page_source:
                    print("UNAVAILABLE: " + row["Link"])
                    row["Title"] = "UNAVAILABLE " + row["Title"]
            writer.writerow(row)
            print(
                "Processed rows: " + str(reader.line_num) + " out of " + str(num_lines)
            )
driver.quit()
