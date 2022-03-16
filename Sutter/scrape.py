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


def process_chargemaster(cms_certification_num, url):
    resp = requests.get(url)
    print(resp.url)

    first_newline_at = resp.text.index("\n")

    s_f = StringIO(resp.text[first_newline_at + 1 :])

    csv_reader = csv.DictReader(s_f)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    for in_row in csv_reader:
        payers = list(in_row.keys())[6:]

        code = in_row.get("CPT")
        if code == "":
            code = "NONE"

        code_disambiguator = in_row.get("ID")

        rev_code = in_row.get("REVENUE_CODE")
        if rev_code == "":
            rev_code = "NONE"

        inpatient_outpatient = in_row.get("SERVICE_SETTING")
        description = in_row.get("DESCRIPTION")

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "code_disambiguator": code_disambiguator,
        }

        for payer in payers:
            price = in_row.get(payer)

            if price == "":
                continue

            if payer == "Gross Charge":
                payer = "GROSS CHARGE"
            elif payer == "Discounted Cash Price":
                payer = "CASH PRICE"
            elif payer == "Minimum Negotiated Price":
                payer = "MIN"
            elif payer == "Maximum Negotiated Price":
                payer = "MAX"

            price = price.replace("$", "").replace(",", "").strip()

            out_row["price"] = price
            out_row["payer"] = payer

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()


def main():
    targets = {
        "054096": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1952350944_SUTTER-CENTER-FOR-PSYCHIATRY_standardcharges.csv",
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.sutterhealth.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
