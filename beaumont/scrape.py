#!/usr/bin/python3

import csv
import http.client
from pprint import pprint
from io import StringIO
import logging
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
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return filename

def fix_price(price_str):
    price_str = price_str.replace("$", "").replace(",", "").strip()

    if "." in price_str and len(price_str.split(".")[-1]) > 2:
        price_str = price_str.split(".")[0] + "." + price_str.split(".")[-1][:2]

    return price_str


def process_chargemaster(cms_certification_num, url):
    filename = download_chargemaster(url)

    in_f = open(filename, "r", encoding="cp1252")
    next(in_f)

    csv_reader = csv.DictReader(in_f)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    for in_row in csv_reader:
        pprint(in_row)
        payers = list(in_row.keys())[5:]

        code = in_row.get("CODE")
        if code == "":
            code = "NONE"

        internal_revenue_code = in_row.get("REV_CODE")
        if internal_revenue_code == "":
            internal_revenue_code = "NONE"

        description = list(in_row.values())[4]
        description = description.strip()

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": internal_revenue_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": description,
        }

        for payer in payers:
            price = in_row.get(payer)
            price = price.strip()
            if not price.startswith("$"):
                continue

            if payer == " GROSS CHARGE  ":
                payer = "GROSS CHARGE"
            elif payer == " DISCOUNTED CASH PRICE  ":
                payer = "CASH PRICE"
            elif payer == " DE-IDENTIFIED  MINIMUM  ":
                payer = "MIN"
            elif payer == " DE-IDENTIFIED MAXIMUM   ":
                payer = "MAX"
            else:
                payer = payer.strip()

            out_row["payer"] = payer
            out_row["price"] = fix_price(price)

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()
    in_f.close()

def main():
    http.client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    targets = {
        "230130": "https://www.beaumont.org/docs/default-source/default-document-library/cdm-documents/2022/hospital-charges/381459362_beaumont-hospital-royal-oak_hospital-standardcharges.csv?sfvrsn=f0427dfb_2&download=true",
        "230142": "https://www.beaumont.org/docs/default-source/default-document-library/cdm-documents/2022/hospital-charges/381405141_beaumont-hospital-wayne_hospital-standardcharges.csv?sfvrsn=e4427dfb_2&download=true",
        "230151": "https://www.beaumont.org/docs/default-source/default-document-library/cdm-documents/2022/hospital-charges/381426919_beaumont-hospital-farmington-hills_hospital-standardcharges.csv?sfvrsn=c0427dfb_2&download=true",
        "230176": "https://www.beaumont.org/docs/default-source/default-document-library/cdm-documents/2022/hospital-charges/381405141_beaumont-hospital-trenton_hospital-standardcharges.csv?sfvrsn=fc427dfb_2&download=true",
        "230269": "https://www.beaumont.org/docs/default-source/default-document-library/cdm-documents/2022/hospital-charges/381459362_beaumont-hospital-troy_hospital-standardcharges.csv?sfvrsn=c8427dfb_2&download=true",
        "230270": "https://www.beaumont.org/docs/default-source/default-document-library/cdm-documents/2022/hospital-charges/381405141_beaumont-hospital-taylor_hospital-standardcharges.csv?sfvrsn=f4427dfb_2&download=true",
        "230020": "https://www.beaumont.org/docs/default-source/default-document-library/cdm-documents/2022/hospital-charges/381405141_beaumont-hospital-dearborn_hospital-standardcharges.csv?sfvrsn=cc427dfb_2&download=true",
        "230089": "https://www.beaumont.org/docs/default-source/default-document-library/cdm-documents/2022/hospital-charges/381459362_beaumont-hospital-grosse-pointe_hospital-standardcharges.csv?sfvrsn=f8427dfb_2&download=true"
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.beaumont.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
