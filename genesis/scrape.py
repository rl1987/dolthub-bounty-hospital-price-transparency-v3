#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint

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

def process_chargemaster(cms_certification_num, url):
    resp = requests.get(url)
    print(resp.url)

    csv_reader = csv.DictReader(StringIO(resp.text))

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()
    
    for in_row in csv_reader:
        payers = list(in_row.keys())[6:]

        code = in_row.get("HCPCS_CODE")
        if code == "":
            code = "NONE"

        rev_code = in_row.get("REVENUE_CODE")
        if rev_code == "":
            rev_code = "NONE"

        code_disambiguator = in_row.get("CDM")

        description = in_row.get("DESCRIPTION")

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
            price = in_row.get(payer).strip()
            if price == "" or price == "n/a" or price == "N/A":
                break

            price = price.replace(",", "")

            if payer == "CHARGES":
                payer = "GROSS CHARGE"
            elif payer == "CASH_AMOUNT":
                payer = "CASH PRICE"
            elif payer == "BLIND_LOW":
                payer = "MIN"
            elif payer == "BLIND_HIGH":
                payer = "MAX"

            out_row['price'] = price
            out_row['payer'] = payer

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()

def main():
    targets = {
        "141304": "https://www.genesishealth.com/app/files/public/581badec-0045-4635-927c-0a357631ae64/454475683_genesis-health-system-aledo_standardcharges.csv",
        "160033": "https://www.genesishealth.com/app/files/public/0a1eebe1-6861-4be6-a92f-137dd11ab126/421418847_genesis-health-system-davenport_standardcharges.csv",
        "161313": "https://www.genesishealth.com/app/files/public/bca0bfc1-04c3-4f7d-ae31-7efac1e2aca1/421418847_genesis-health-system-dewitt_standardcharges.csv",
        "140275": "https://www.genesishealth.com/app/files/public/ceb6b4ee-5145-45b3-8839-20e2185daf7b/363616314_genesis-health-system-silvis_standardcharges.csv",
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write('UPDATE `hospitals` SET `homepage_url` = "https://www.genesishealth.com/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(url, cms_id))

    h_f.close()

if __name__ == "__main__":
    main()

