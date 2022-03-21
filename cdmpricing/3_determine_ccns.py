#!/usr/bin/python3

import csv
from glob import glob
from pprint import pprint
import sys

import doltcli as dolt

FIELDNAMES = [ "cdm_id", "name", "ccn", "db_name" ]

def main():
    if len(sys.argv) == 2:
        db = dolt.Dolt(sys.argv[1])
    else:
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    out_f = open("ccns.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    counts = dict()

    not_found = []

    for f in glob("*.csv"):
        if f.startswith("moz-") or f == "ccns.csv":
            continue

        in_f = open(f, "r", encoding="utf-8")
        csv_reader = csv.DictReader(in_f)
        try:
            first_row = next(csv_reader)
        except:
            in_f.close()
            continue
        in_f.close()
    
        cdm_id = first_row.get("cdm_id")
        name = first_row.get("hospital_name")

        res = db.sql('SELECT * FROM `hospitals` WHERE `name` LIKE "%{}%" AND `last_edited_by_username` IS NULL;'.format(name),
                result_format="json")
        pprint(res)

        if len(res["rows"]) == 1:
            ccn = res["rows"][0]["cms_certification_num"]
            db_name = res["rows"][0]["name"]

            out_row = {
                "cdm_id": cdm_id,
                "name": name,
                "ccn": ccn,
                "db_name": db_name
            }

            pprint(out_row)
            csv_writer.writerow(out_row)

            if counts.get(ccn) is None:
                counts[ccn] = 1
            else:
                counts[ccn] += 1
        else:
            not_found.append((cdm_id, name))

    out_f.close()

    print("Counts:")
    pprint(counts)
    print("Not found:")
    pprint(not_found)

if __name__ == "__main__":
    main()

