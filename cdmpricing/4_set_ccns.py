#!/usr/bin/python3

import csv
from glob import glob
from pprint import pprint
import sys

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
    cdm_id_to_ccn = dict()

    in_f = open("ccns.csv", "r", encoding="utf-8")
    csv_reader = csv.DictReader(in_f)

    for row in csv_reader:
        pprint(row)
        cdm_id = row.get("cdm_id")
        ccn = row.get("ccn")

        cdm_id_to_ccn[cdm_id] = ccn

    in_f.close()

    pprint(cdm_id_to_ccn)

    for f in glob("*.csv"):
        if f.startswith("moz-") or f == "ccns.csv":
            continue

        in_f = open(f, "r", encoding="utf-8")

        csv_reader = csv.DictReader(in_f)

        out_f = open("out_" + f, "w", encoding="utf-8")

        csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
        csv_writer.writeheader()

        for in_row in csv_reader:
            ccn = cdm_id_to_ccn.get(in_row.get('cdm_id'))
            if ccn is None:
                continue

            out_row = dict(in_row)

            del out_row['cdm_id']
            del out_row['hospital_name']

            out_row['cms_certification_num'] = ccn

            csv_writer.writerow(out_row)

        out_f.close()

if __name__ == "__main__":
    main()

