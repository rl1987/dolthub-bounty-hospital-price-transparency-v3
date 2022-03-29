#!/usr/bin/python3

import csv
from pprint import pprint

from lxml import html
import requests

FIELDNAMES = ["url", "name", "cdm_url", "homepage_url"]


def main():
    in_f = open(
        "moz-inbound-links-for-pricetransparency_accureg_net-2022-03-29_09_55_24_080947Z.csv",
        "r",
    )
    csv_reader = csv.reader(in_f)

    out_f = open("todo.csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    seen_urls = set()

    for row in csv_reader:
        if len(row) != 17:
            continue

        url = row[7]
        if url == "Target URL":
            continue

        url = "https://" + url

        if url in seen_urls:
            continue

        seen_urls.add(url)

        resp = requests.get(url)
        print(resp.url)

        tree = html.fromstring(resp.text)

        homepage_url = row[0]

        for dl_row in tree.xpath('//div[@class="ptdownloadrow"]'):
            name = dl_row.xpath('.//div[@class="ptdownloadrowfacilityname"]/text()')
            if len(name) == 0:
                continue

            name = name[0]
            name = name.split(" - ")[0]

            cdm_url = dl_row.xpath('.//a[contains(@href, ".csv")]/@href')
            if len(cdm_url) == 0:
                continue

            cdm_url = cdm_url[0]

            row = {
                "url": url,
                "name": name,
                "cdm_url": cdm_url,
                "homepage_url": homepage_url,
            }

            pprint(row)
            csv_writer.writerow(row)

    in_f.close()
    out_f.close()


if __name__ == "__main__":
    main()
