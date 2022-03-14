#!/usr/bin/python3

import csv
from pprint import pprint
from io import BytesIO
import json
from urllib.request import urlretrieve

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


def main():
    cms_certification_num = "030131"

    url = "https://oasishospital.com/wp-content/uploads/2022/02/271397457OASISHospitalstandardcharges.json"
    dest_path = "charges.json"

    urlretrieve(url, dest_path)

    in_f = open("charges.json", "r")
    json_dict = json.load(in_f)
    in_f.close()

    out_f = open("030131.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    disamb = dict()

    for data_dict in json_dict.get("data"):
        if len(data_dict) == 0:
            continue

        data_dict = data_dict[0]
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
        code_disambiguator = disamb.get(code)
        if code_disambiguator is None:
            code_disambiguator = 1
        else:
            code_disambiguator += 1

        disamb[code] = code_disambiguator

        row = {
            "cms_certification_num": cms_certification_num,
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

    out_f.close()


if __name__ == "__main__":
    main()
