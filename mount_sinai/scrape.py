#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint
import re

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


def is_number(price):
    return re.match("\d+(\.\d{2})", price) is not None


def process_chargemaster(cms_id, url):
    resp = requests.get(url)
    print(resp.url)

    s_f = StringIO(resp.text)

    out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    csv_reader = csv.reader(s_f)

    gross_prices = dict()
    discounted_prices = dict()

    next(csv_reader)
    next(csv_reader)
    next(csv_reader)

    min_rates = dict()
    max_rates = dict()

    desc_to_code = dict()

    for in_row in csv_reader:
        payer = in_row[1]
        code = str(in_row[2])
        description = in_row[3].strip()
        gross = in_row[4]
        discounted = in_row[5]
        negotiated = in_row[6]
        negotiated_min = in_row[7]
        negotiated_max = in_row[8]

        if code.endswith(".0"):
            code = code.replace(".0", "")

        if type(discounted) == str:
            discounted = discounted.replace("$", "").replace(",", "").strip()

        desc_to_code[description] = code

        out_row = {
            "cms_certification_num": cms_id,
            "code": code,
            "internal_revenue_code": "NONE",
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": description,
        }

        if is_number(gross) and gross_prices.get(code) is None:
            out_row["payer"] = "GROSS CHARGE"
            out_row["price"] = gross
            pprint(out_row)
            csv_writer.writerow(out_row)

            gross_prices[code] = gross

        if is_number(discounted) and discounted_prices.get(code) is None:
            out_row["payer"] = "CASH PRICE"
            out_row["price"] = discounted
            pprint(out_row)
            csv_writer.writerow(out_row)

            discounted_prices[code] = discounted

        if is_number(negotiated):
            out_row["payer"] = payer
            out_row["price"] = negotiated
            pprint(out_row)
            csv_writer.writerow(out_row)

        if is_number(negotiated_min):
            prev_min = min_rates.get(description)
            if prev_min is None or negotiated_min < prev_min:
                min_rates[description] = negotiated_min

        if is_number(negotiated_max):
            prev_max = max_rates.get(description)
            if prev_max is None or negotiated_max > prev_max:
                max_rates[description] = negotiated_max

    for description in desc_to_code.keys():
        code = desc_to_code[description]

        out_row = {
            "cms_certification_num": cms_id,
            "code": code,
            "internal_revenue_code": "NONE",
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": description,
        }

        min_rate = min_rates.get(description)
        if min_rate is not None:
            out_row["payer"] = "MIN"
            out_row["price"] = min_rate
            pprint(out_row)
            csv_writer.writerow(out_row)

        max_rate = max_rates.get(description)
        if max_rate is not None:
            out_row["payer"] = "MAX"
            out_row["price"] = max_rate
            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()


def main():
    targets = {
        "330024": "https://www.mountsinai.org/files/MSHealth/Assets/HS/About/Insurance/131624096_mount-sinai-hospital_standardcharges.csv",
        "330169": "https://www.mountsinai.org/files/MSHealth/Assets/HS/About/Insurance/135564934_mount-sinai-beth-israel_standardcharges.csv",
        "330046": "https://www.mountsinai.org/files/MSHealth/Assets/HS/About/Insurance/132997301_mount-sinai-morningside_west_standardcharges.csv",
        "330198": "https://www.mountsinai.org/files/MSHealth/Assets/HS/About/Insurance/111352310_mount-sinai-south-nassau_standardcharges.csv",
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.mountsinai.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
