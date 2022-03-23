#!/usr/bin/python3

import csv
from pprint import pprint
import os

import requests

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

def download_chargemaster(url):
    filename = url.split("/")[-1]

    if os.path.isfile(filename):
        print("{} already downloaded".format(filename))
        return filename

    print("Downloading: {} -> {}".format(url, filename))
    
    # Based on: https://stackoverflow.com/a/16696317
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return filename

def process_chargemaster(cms_id, url):
    filename = download_chargemaster(url)

    out_f = open("out_{}.csv".format(cms_id), "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    in_f = open(filename, "r", encoding="cp1252")

    csv_reader = csv.DictReader(in_f)

    for in_row in csv_reader:
        pprint(in_row)

        code = in_row.get("ProcedureCode")
        if code == "N/A":
            code = "NONE"

        modifier = in_row.get("Modifier")
        if modifier != "N/A":
            code += "-" + modifier

        rev_code = in_row.get("RevenueCode")
        if rev_code == "N/A":
            rev_code = "NONE"

        description = in_row.get("Description")

        out_row = {
            "cms_certification_num": cms_id,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "code_disambiguator": "NONE"
        }

        payers = list(in_row.keys())[8:]
        pprint(payers)

        for payer in payers:
            price = in_row.get(payer)
            if price == "N/A":
                continue

            inpatient_outpatient = "UNSPECIFIED"

            if payer == "InpatientGrossCharge":
                payer = "GROSS CHARGE"
                inpatient_outpatient = "INPATIENT"
            elif payer == "OutpatientGrossCharge":
                payer = "GROSS CHARGE"
                inpatient_outpatient = "OUTPATIENT"
            elif payer == "DiscountedCashPriceInpatient":
                payer = "CASH PRICE"
                inpatient_outpatient = "INPATIENT"
            elif payer == "DiscountedCashPriceOutpatient":
                payer = "CASH PRICE"
                inpatient_outpatient = "OUTPATIENT"
            elif payer == "MinimumNegotiatedCharge":
                payer = "MIN"
            elif payer == "MaximumNegotiatedCharge":
                payer = "MAX"
            elif payer.endswith("_OPPS"):
                payer = payer.replace("_OPPS", "")
                inpatient_outpatient = "OUTPATIENT"
            elif payer.endswith("_IPPS"):
                payer = payer.replace("_IPPS", "")
                inpatient_outpatient = "INPATIENT"
            else:
                continue

            out_row['price'] = price
            out_row['payer'] = payer
            out_row['inpatient_outpatient'] = inpatient_outpatient

            pprint(out_row)
            csv_writer.writerow(out_row)

    in_f.close()
    out_f.close()

def main():
    in_f = open("todo2.csv", "r")
    csv_reader = csv.DictReader(in_f)

    h_f = open('hospitals.sql', 'w')
        
    for row in csv_reader:
        process_chargemaster(row.get("ccn"), row.get("cdm_url"))
        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "{}", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                row.get("homepage_url"), row.get("cdm_url"), row.get("ccn")
            )
        )

    in_f.close()

if __name__ == "__main__":
    main()

