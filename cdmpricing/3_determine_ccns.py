#!/usr/bin/python3

import csv
from glob import glob
from pprint import pprint
import sys

import doltcli as dolt

FIELDNAMES = [ "cdm_id", "name", "ccn", "db_name" ]

OVERRIDES = {
    "80a6ed58c67c09453664811584bad805": "140054",
    "94b5b87a820d24357021991027b5be87": "220100",
    "58f6ace02d1ae1bffca56d18d40fb1df": "140166",
    "e541183863a90b1bd92e5225829d0ea9": "260175",
    "174b78499809efe20c75cf407c3298d6": "341320",
    "322271e40f3bb97f178309b75df38cc9": "061302",
    "b830fe8bf0b68872cce67a28b7b3c3ab": "310021",
    "e6d322b39e32a0ef6a713b0127a22def": "390156",
    "e15f43d5f85082ad98a1aed8519dfbb8": "210004",
    "0df4b82428877de5f673897a97cc8f17": "330406",
    "bc654c8653dfd4a84145b1f1abc0e2f6": "050289",
    "af4369c01c9f4ed50a279839e12e32eb": "530012",
    "2cdebd3b64c0882116cd2a1345337713": "100181",
    "2681662fb48ed3ef7b21f25c934ad1b4": "450253",
    "5a694066d76b01081f2dc12cb7d912a9": "330180",
    "66fc13e48cb7f95b6744c2455e5f13af": "220108"
}

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

        ccn = OVERRIDES.get(cdm_id)

        if len(res["rows"]) == 1 or ccn is not None:
            if ccn is None:
                ccn = res["rows"][0]["cms_certification_num"]
                db_name = res["rows"][0]["name"]
            else:
                db_name = ""

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

