#!/usr/bin/python3

import csv
from io import StringIO
from pprint import pprint

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

def fix_price(price_str):
    price_str = price_str.replace("$", "").replace(",", "").strip()

    if "." in price_str and len(price_str.split(".")[-1]) > 2:
        price_str = price_str.split(".")[0] + "." + price_str.split(".")[-1][:2]

    return price_str

def process_chargemaster(cms_certification_num, url):
    resp = requests.get(url)
    print(resp.url)

    if resp.text.startswith("CPT,Description"): # HACK to fix duplicate field names
        resp.text = resp.text.replace("CPT,Description", "SVCCD,Description")

    s_f = StringIO(resp.text)

    csv_reader = csv.DictReader(s_f)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    for in_row in csv_reader:
        code = in_row.get('CPT').strip()
        if code == "":
            code = "NONE"

        description = in_row.get("Description").strip()
        code_disambiguator = in_row.get("SVCCD")
        
        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": "NONE",
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": code_disambiguator
        }

        payers = list(in_row.keys())[3:]
        
        for payer in payers:
            if payer == "As of Date":
                continue

            price = in_row.get(payer)

            if price == "" or price is None:
                continue

            price = fix_price(price)

            if payer == "DISCOUNTED CASH PRICE INPATIENT":
                out_row['inpatient_outpatient'] = "INPATIENT"
                out_row['payer'] = "CASH PRICE"
                out_row['price'] = price
                pprint(out_row)
                csv_writer.writerow(out_row)
                out_row['inpatient_outpatient'] = "UNSPECIFIED"
            elif payer == "DISCOUNTED CASH PRICE OUTPATIENT":
                out_row['inpatient_outpatient'] = "OUTPATIENT"
                out_row['payer'] = "CASH PRICE"
                out_row['price'] = price
                pprint(out_row)
                csv_writer.writerow(out_row)
                out_row['inpatient_outpatient'] = "UNSPECIFIED"
            elif payer == "Gross Charge":
                out_row['payer'] = "GROSS CHARGE"
                out_row['price'] = price
                pprint(out_row)
                csv_writer.writerow(out_row)
            elif payer == "DE-IDENTIFIED MIN":
                out_row['payer'] = "MIN"
                out_row['price'] = price
                pprint(out_row)
                csv_writer.writerow(out_row)
            elif payer == "DE-IDENTIFIED MAX":
                out_row['payer'] = "MAX"
                out_row['price'] = price
                pprint(out_row)
                csv_writer.writerow(out_row)
            else:
                out_row['payer'] = payer
                out_row['price'] = price

    out_f.close()

def main():
    in_f = open("ccn.csv", "r")

    csv_reader = csv.DictReader(in_f)

    h_f = open("hospitals.sql", "w")

    for row in csv_reader:
        process_chargemaster(row.get('ccn'), row.get('cdm_url'))
        h_f.write( 'UPDATE `hospitals` SET `homepage_url` = "{}", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(row.get('web_url'), row.get('cdm_url'), row.get('ccn')))

    h_f.close()
    in_f.close()

if __name__ == "__main__":
    main()

