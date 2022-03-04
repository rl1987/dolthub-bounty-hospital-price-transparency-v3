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

    b_f = StringIO(resp.text)

    csv_reader = csv.reader(b_f)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

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
            "inpatient_outpatient": "UNSPECIFIED",
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

def main():
    targets = {
        "032006": "https://kpcph.com/wp-content/uploads/2022/02/83-4169286_KPC-Promise-Hospital-of-Phoenix-LLC_standardcharges.csv",
        #"192004": "https://kpcph.com/wp-content/uploads/2022/02/83-4190159_KPC-Promise-Hospital-of-Baton-Rouge-LLC_standardcharges.csv",
        "172004": "https://kpcph.com/wp-content/uploads/2022/02/83-4307959_KPC-Promise-Hospital-of-Overland-Park-LLC_standardcharges.csv",
        "252008": "https://kpcph.com/wp-content/uploads/2022/02/83-4225974_KPC-Promise-Hospital-of-Vicksburg-LLC_standardcharges.csv",
        "462004": "https://kpcph.com/wp-content/uploads/2022/02/83-4141873_KPC-Promise-Hospital-of-Salt-Lake-LLC_standardcharges.csv",
        "452067": "https://kpcph.com/wp-content/uploads/2022/02/83-4250847_KPC-Promise-Hospital-of-Dallas-LLC_standardcharges.csv",
        "452068": "https://kpcph.com/wp-content/uploads/2022/02/83-4295134_KPC-Promise-Hospital-of-Wichita-Falls-LLC_standardcharges.csv"
    }

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

if __name__ == "__main__":
    main()
