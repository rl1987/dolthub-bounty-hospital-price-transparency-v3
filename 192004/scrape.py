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


def main():
    cms_certification_num = "192004"

    resp = requests.get(
        "https://kpcph.com/wp-content/uploads/2022/02/83-4190159_KPC-Promise-Hospital-of-Baton-Rouge-LLC_standardcharges.csv"
    )
    print(resp.url)

    b_f = StringIO(resp.text)

    csv_reader = csv.reader(b_f)

    out_f = open("192004.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    next(csv_reader)
    next(csv_reader)
    next(csv_reader)
    next(csv_reader)

    for in_row in csv_reader:
        if len(in_row) < 4:
            continue

        code = in_row[0]
        description = in_row[1]
        gross = in_row[2]
        discounted = in_row[3]

        out_row = {
            "cms_certification_num": cms_certification_num,
            "payer": "CASH PRICE",
            "code": "NONE",
            "internal_revenue_code": code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "INPATIENT",  # XXX: is this right?
            "price": discounted,
            "code_disambiguator": "NONE",
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

        out_row["payer"] = "LIST PRICE"
        out_row["price"] = gross

        pprint(out_row)
        csv_writer.writerow(out_row)

    b_f.close()
    out_f.close()


if __name__ == "__main__":
    main()
