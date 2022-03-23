#!/usr/bin/python3

import csv
import sys
from pprint import pprint

import doltcli as dolt

FIELDNAMES = [
    'url', 'name', 'cdm_url', 'homepage_url', 'ccn'
]

OVERRIDES = {
    "https://pricetransparency.blob.core.windows.net/uabmedicalwest/721608375_medicalwesthospital_standardcharges.csv": "010114",
    "https://pricetransparency.blob.core.windows.net/archbold/58-6001901_mitchellcountyhospital_standardcharges.csv": "111331"
}

def main():
    if len(sys.argv) == 2:
        db = dolt.Dolt(sys.argv[1])
    else:
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    counts = dict()

    in_f = open("todo.csv", "r", encoding="utf-8")

    csv_reader = csv.DictReader(in_f)
    
    out_f = open("todo2.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator='\n')
    csv_writer.writeheader()

    for in_row in csv_reader:
        name = in_row.get('name')
        cdm_url = in_row.get('cdm_url')

        res = db.sql('SELECT * FROM `hospitals` WHERE `name` LIKE "%{}%" AND `last_edited_by_username` IS NULL;'.format(name),
                result_format="json")
        pprint(res)

        ccn = OVERRIDES.get(cdm_url)

        if len(res["rows"]) == 1 or ccn is not None:
            out_row = dict(in_row)
            if ccn is None:
                ccn = res["rows"][0]["cms_certification_num"]
            out_row['ccn'] = ccn

            pprint(out_row)
            csv_writer.writerow(out_row)

            if counts.get(ccn) is None:
                counts[ccn] = 1
            else:
                counts[ccn] += 1
        else:
            print("Not found: ", name)

    in_f.close()

if __name__ == "__main__":
    main()

