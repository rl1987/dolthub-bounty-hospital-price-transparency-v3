#!/usr/bin/python3

import csv
import sys
from urllib.parse import urlparse

def main():
    in_f = open(sys.argv[1], "r")

    cdm_ids = set()

    csv_reader = csv.reader(in_f)

    for row in csv_reader:
        if len(row) != 17:
            continue

        cdm_url = row[7]
        if cdm_url == "Target URL":
            continue

        print(cdm_url)
        cdm_id = cdm_url.split('/')[1]

        if cdm_id != "":
            cdm_ids.add(cdm_id)

    in_f.close()

    out_f = open("cdm_ids.txt", "w")

    for cdm_id in cdm_ids:
        out_f.write(cdm_id + "\n")

    out_f.close()

if __name__ == "__main__":
    main()

