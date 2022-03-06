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
    cms_certification_num = "013300"

    resp = requests.get("https://www.childrensal.org/workfiles/Billing/630307306_ChildrensOfAlabama_StandardCharges.csv")
    print(resp.url)

    s_f = StringIO(resp.text)

    csv_reader = csv.DictReader(s_f)
    
    out_f = open("013300.csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    disamb = dict()

    for in_row in csv_reader:
        pprint(in_row)
        
        payers = list(in_row.keys())[7:]

        code = in_row.get("HCPCS/CPT").strip()
        if code == '':
            code = "NONE"

        rev_code = in_row.get("RevCd").strip()
        if rev_code == '':
            rev_code = "NONE"
        
        description = in_row.get("RevCd - Description").strip()
        
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

            if price == "*See Narrative":
                continue

            payer = payer.strip()

            if payer == "Gross Charge":
                payer = "GROSS CHARGE"

            if payer == "Cash Price":
                payer = "CASH PRICE"

            if payer == "Min Neg. Rate":
                payer = "MIN"

            if payer == "Max Neg. Rate":
                payer = "MAX"

            out_row['payer'] = payer
            out_row['price'] = price

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()

if __name__ == "__main__":
    main()

