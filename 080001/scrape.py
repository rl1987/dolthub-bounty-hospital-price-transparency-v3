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
    cms_certification_num = "080001"

    resp = requests.get("https://billing.christianacare.org/media/4/download?attachment")
    print(resp.url)

    s_f = StringIO(resp.text)

    csv_reader = csv.DictReader(s_f)
    
    out_f = open("080001.csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    disamb = dict()

    for in_row in csv_reader:
        pprint(in_row)
        
        payers = list(in_row.keys())[3:]

        code = in_row.get("HCPC").strip()
        if code == '':
            code = "NONE"

        rev_code = in_row.get("RC").strip()
        if rev_code == '':
            rev_code = "NONE"
        
        description = in_row.get("\ufeffService").strip()
        
        if disamb.get(code) is None:
            code_disambiguator = 1
            disamb[code] = code_disambiguator
        else:
            code_disambiguator = disamb[code] + 1
            disamb[code] = code_disambiguator

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": code_disambiguator
        }

        for payer in payers:
            price = in_row.get(payer).replace(",", "").strip()
            if price == '':
                continue

            if "-" in price:
                continue

            payer = payer.strip()

            if payer == "Price":
                payer = "GROSS CHARGE"

            if payer == "Cash Price":
                payer = "CASH PRICE"

            if payer == "Minimum":
                payer = "MIN"

            if payer == "Maximum":
                payer = "MAX"

            if type(price) == str:
                price = price.replace("$", "").replace(",", "").strip()

            out_row['payer'] = payer
            out_row['price'] = price

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()
    # https://github.com/BurntSushi/xsv
    # $ xsv split --size 100000 . 080001.csv 

if __name__ == "__main__":
    main()

