#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint
import re
import os
import json

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

def process_chargemaster(cms_id, url):
    filename = download_chargemaster(url)

    in_f = open(filename, "r", encoding="cp1252")

    json_dict = json.load(in_f)

    resp = requests.get(url)
    print(resp.url)

    out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for data_dict in json_dict.get("data"):
        if len(data_dict) == 0:
            continue

        data_dict = data_dict[-1]
        description = data_dict.get("code description")
        if description is None:
            continue

        code = data_dict.get("code")
        code_type = data_dict.get("code type")
        payer = data_dict.get("payer")
        gross = data_dict.get("gross charge")
        discounted = data_dict.get("discounted cash price")
        min_price = data_dict.get("de-identified minimum negotiated charge")
        max_price = data_dict.get("de-identified maximum negotiated charge")
        code_disambiguator = "NONE"

        row = {
            "cms_certification_num": cms_id,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": str(code_disambiguator),
        }

        if code_type == "revCode":
            row["code"] = "NONE"
            row["internal_revenue_code"] = code
        else:
            row["code"] = code
            row["internal_revenue_code"] = "NONE"

        if gross is not None:
            row["payer"] = "GROSS CHARGE"
            row["price"] = gross
            pprint(row)
            csv_writer.writerow(row)

        if discounted is not None:
            row["payer"] = "CASH PRICE"
            row["price"] = discounted
            pprint(row)
            csv_writer.writerow(row)

        if min_price is not None:
            row["payer"] = "MIN"
            row["price"] = min_price
            pprint(row)
            csv_writer.writerow(row)

        if max_price is not None:
            row["payer"] = "MAX"
            row["price"] = max_price
            pprint(row)
            csv_writer.writerow(row)

    in_f.close()
    out_f.close()

def main():
    targets = {
        "450002": "https://www.thehospitalsofprovidence.com/docs/global/standard-charges/954537720_thehospitalsofprovidencememorialcampus_standardcharges.json?sfvrsn=4b2ad6a7_8&download=true",
        "670047": "https://www.thehospitalsofprovidence.com/docs/global/standard-charges/954537720_thehospitalsofprovidenceeastcampus_standardcharges.json?sfvrsn=2b76b1e7_8&download=true",
        "670120": "https://www.thehospitalsofprovidence.com/docs/global/standard-charges/954537720_thehospitalofprovidencetransmountaincampus_standardcharges.json?sfvrsn=fd47d09f_8&download=true",
        "450668": "https://www.thehospitalsofprovidence.com/docs/global/standard-charges/954537720_thehospitalsofprovidencesierracampus_standardcharges.json?sfvrsn=803dfdaa_8&download=true"
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.thehospitalsofprovidence.com", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
