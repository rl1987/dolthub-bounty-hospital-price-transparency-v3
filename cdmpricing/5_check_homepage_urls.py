#!/usr/bin/python3

import csv
from pprint import pprint
import sys

import doltcli as dolt
from lxml import html
import requests

FIELDNAMES = ["cms_certification_num", "name", "homepage_url", "status_code", "title"]


def main():
    if len(sys.argv) == 2:
        db = dolt.Dolt(sys.argv[1])
    else:
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    out_f = open("homepages.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    res = db.sql(
        'SELECT * FROM `hospitals` WHERE `chargemaster_url` LIKE "%cdmpricing%";',
        result_format="json",
    )

    pprint(res)

    for db_row in res["rows"]:
        cms_certification_num = db_row["cms_certification_num"]
        name = db_row["name"]
        homepage_url = db_row["homepage_url"]

        status_code = -1
        title = ""

        try:
            resp = requests.get(homepage_url, timeout=1)
            print(resp.url)
            status_code = resp.status_code
            tree = html.fromstring(resp.text)
            title = tree.xpath("//title/text()")[0]
        except Exception as e:
            pprint(e)
            pass

        out_row = {
            "cms_certification_num": cms_certification_num,
            "name": name,
            "homepage_url": homepage_url,
            "status_code": status_code,
            "title": title,
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

    out_f.close()


if __name__ == "__main__":
    main()
