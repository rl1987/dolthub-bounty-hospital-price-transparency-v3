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

def scrape_hospital_data(cms_certification_num, xlsx_url, csv_writer):
    resp = requests.get(xlsx_url)
    print(resp)
    print(resp.url)

    b_f = BytesIO(resp.content)

    wb = openpyxl.load_workbook(b_f)
    ws = wb.active
    
    for in_row in ws.rows:
        if len(in_row) < 4:
            continue
        
        if in_row[0].value == "CDM\nNumber":
            continue

        description = in_row[1].value
        code = in_row[2].value
        rev_code = in_row[3].value
        price = in_row[4].value

        if type(code) == float or type(code) == int:
            code = str(int(code))

        code = code.strip()

        if code is None or (type(code) == str and code == ""):
            code = "NONE"

        if rev_code is None or rev_code == "":
            rev_code = "NONE"

        if price is None or price == "Charges":
            continue

        out_row = {
            "cms_certification_num": cms_certification_num,
            "payer": "GROSS CHARGES",
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "price": price,
            "code_disambiguator": int(in_row[0].value)
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

    b_f.close()

def main():
    targets = {
        "051319": "https://www.dignityhealth.org/content/dam/dignity-health/documents/legal/cdm-files-2021/ein_mercymedicalcentershasta_standardcharges.xlsx",
        "050280": "https://www.dignityhealth.org/content/dam/dignity-health/documents/legal/cdm-files-2021/ein_mercymedicalcenterredding_standardcharges.xlsx",
        "050042": "https://www.dignityhealth.org/content/dam/dignity-health/documents/legal/cdm-files-2021/ein_stelizabethcommunityhospital_standardcharges.xlsx",
    }

    for csm_num in targets.keys():
        out_f = open("{}.csv".format(csm_num), "w", encoding="utf-8")

        csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
        csv_writer.writeheader()

        xlsx_url = targets[csm_num]

        scrape_hospital_data(csm_num, xlsx_url, csv_writer)

        out_f.close()

if __name__ == "__main__":
    main()
