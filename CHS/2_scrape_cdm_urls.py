#!/usr/bin/python3

import csv
from pprint import pprint
from urllib.parse import urljoin

import requests
from lxml import html

FIELDNAMES = [
    "name",
    "street_addr",
    "city",
    "state",
    "zipcode",
    "phone",
    "bed_count",
    "web_url",
    "cdm_url",
]

OVERRIDES = {
    "Tennova Healthcare – Clarksville": "http://www.tennovaclarksville.com/",
    "Tennova Healthcare – Cleveland": "http://www.tennovacleveland.com/",
    "Tennova - Jefferson Memorial Hospital": "http://www.tennovajefferson.com/",
    "Tennova - LaFollette Medical Center": "http://www.tennovalafollette.com/",
    "Tennova - Newport Medical Center": "http://www.tennovanewport.com/",
    "Tennova - North Knoxville Medical Center": "http://www.tennovanorthknoxville.com/",
    "Tennova - Turkey Creek Medical Center": "http://www.tennovaturkeycreek.com/",
    "Northwest Health Physicians' Specialty Hospital": "https://www.northwesthealth.com/",
    "Poplar Bluff Regional Medical Center": "https://www.pbrmc.com/",
}


def main():
    in_f = open("locations.csv", "r", encoding="utf-8")

    csv_reader = csv.DictReader(in_f)

    out_f = open("cdm_urls.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for in_row in csv_reader:
        name = in_row.get("name")
        web_url = in_row.get("web_url")
        if OVERRIDES.get(name) is not None:
            web_url = OVERRIDES.get(name)

        transp_url = urljoin(web_url, "/pricing-information")

        resp = requests.get(transp_url)
        print(resp.url, resp.status_code)

        if resp.status_code != 200:
            continue

        tree = html.fromstring(resp.text)

        for cdm_link in tree.xpath('//a[text() = "DOWNLOAD CSV OF CHARGEMASTER"]'):
            cdm_url = urljoin(resp.url, cdm_link.get("href").replace(" ", "%20"))

            out_row = dict(in_row)
            out_row["cdm_url"] = cdm_url

            pprint(out_row)
            csv_writer.writerow(out_row)

    in_f.close()
    out_f.close()


if __name__ == "__main__":
    main()
