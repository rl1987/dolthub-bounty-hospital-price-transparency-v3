#!/usr/bin/python3

import csv
from glob import glob
from pprint import pprint
import sys
import os

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

    cdm_id_to_site = dict()

    in_f = open("moz-inbound-links-for-cdmpricing_com-2022-03-21_09_06_07_330067Z.csv", "r")
    csv_reader = csv.reader(in_f)

    for row in csv_reader:
        if len(row) != 17:
            continue

        cdm_url = row[7]
        if cdm_url == "Target URL":
            continue

        print(cdm_url)
        cdm_id = cdm_url.split('/')[1]

        web_url = row[0]
        web_url = "https://" + web_url.split("/")[0]

        if cdm_id != "":
            cdm_id_to_site[cdm_id] = web_url

    in_f.close()

    pprint(cdm_id_to_ccn)

    h_f = open("hospitals.sql", "w")

    for f in glob("*.csv"):
        if f.startswith("moz-") or f == "ccns.csv" or f.startswith("out_"):
            continue

        in_f = open(f, "r", encoding="utf-8")

        csv_reader = csv.DictReader(in_f)

        out_f = open("out_" + f, "w", encoding="utf-8")

        csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
        csv_writer.writeheader()

        not_found = False

        ccn = None
        cdm_id = None

        for in_row in csv_reader:
            cdm_id = in_row.get("cdm_id")
            ccn = cdm_id_to_ccn.get(cdm_id)
            if ccn is None:
                out_f.close()
                os.unlink("out_" + f)
                not_found = True
                break

            out_row = dict(in_row)

            del out_row['cdm_id']
            del out_row['hospital_name']

            out_row['cms_certification_num'] = ccn

            csv_writer.writerow(out_row)

        if not not_found:
            out_f.close()
    
            if cdm_id is not None and ccn is not None:
                web_url = cdm_id_to_site.get(cdm_id)
                h_f.write('UPDATE `hospitals` SET `homepage_url` = "{}", `chargemaster_url` = "https://www.cdmpricing.com/{}/standard-charges", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(web_url, cdm_id, ccn))

    h_f.close()

if __name__ == "__main__":
    main()

