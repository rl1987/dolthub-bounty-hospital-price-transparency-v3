#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO

import requests
import openpyxl

FIELDNAMES = [
    "cms_certification_num",
    "payer",
    "code",
    "internal_revenue_code",
    "units",
    "description",
    "inpatient_outpatient",
    "price",
    "code_disambiguator",
]


def main():
    cms_certification_num = "010168"

    resp = requests.get(
        "https://pricetransparency.blob.core.windows.net/jackhughston/33-1058243_jackhughstonmemorialhospital_standardcharges.csv"
    )
    print(resp.url)


if __name__ == "__main__":
    main()
