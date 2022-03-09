#!/usr/bin/python3

import csv
from pprint import pprint
from io import BytesIO

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
    cms_certification_num = "050113"

    resp = requests.get("https://www.smchealth.org/sites/main/files/file-attachments/smmc_pricing_2022.xlsx?1640202141")
    print(resp.url)

    b_f = BytesIO(resp.content)

    wb = openpyxl.load_workbook(b_f)
    ws = wb.active

    out_f = open("050113.csv", "w", encoding="utf-8")   

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for row in ws.rows:
        if len(row) < 9:
            continue

        if row[0].value == "CDM":
            continue

        cmd = row[0].value.strip()
        description = row[1].value.strip()
        cpt = row[2].value.strip()
        cur_price = row[4].value
        discounted = row[7].value
        hpsm_rate = row[8].value
        
        print(cur_price, discounted, hpsm_rate)

        if cpt == "-":
            cpt = "NONE"

        out_row = {
            "cms_certification_num": cms_certification_num,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": "NONE",
            "code": cpt,
            "internal_revenue_code": cmd, # XXX: is this right?
        }

        if type(cur_price) == int or type(cur_price) == float:
            out_row["payer"] = "GROSS CHARGE"
            out_row["price"] = cur_price
            pprint(out_row)
            csv_writer.writerow(out_row)

        if type(discounted) == int or type(discounted) == float:
            out_row["payer"] = "CASH PRICE"
            out_row["price"] = discounted
            pprint(out_row)
            csv_writer.writerow(out_row)

        if type(hpsm_rate) == int or type(hpsm_rate) == float:
            out_row["payer"] = "HPSM"
            out_row["price"] = hpsm_rate
            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()

if __name__ == "__main__":
    main()
