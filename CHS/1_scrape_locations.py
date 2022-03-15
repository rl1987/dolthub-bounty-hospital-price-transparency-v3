#!/usr/bin/python3

import csv
import time
from pprint import pprint

import js2xml
import requests

FIELDNAMES = ["name", "street_addr", "city", "zipcode", "phone", "bed_count", "web_url"]


def main():
    params = {"callback": "locationDataCallback", "_": int(time.time())}

    resp = requests.get(
        "https://www.chslocationsmap.com/data/map/default/locations.json", params=params
    )
    print(resp.url)

    parsed = js2xml.parse(resp.text)

    out_f = open("locations.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for h in parsed.xpath('//property[@name="hospitals"]/array/object'):
        name = h.xpath('.//property[@name="name"]/string/text()')[0]
        street_addr = h.xpath('.//property[@name="street"]/string/text()')[0]
        city = h.xpath('.//property[@name="city"]/string/text()')[0]
        zipcode = h.xpath('.//property[@name="zip"]/string/text()')[0]
        phone = h.xpath('.//property[@name="phone"]/string/text()')[0]
        if "<" in phone:
            phone = None

        try:
            bed_count = h.xpath('.//property[@name="bedCount"]/number/@value')[0]
        except:
            bed_count = None

        web_url = h.xpath('.//property[@name="websiteUrl"]/string/text()')[0]

        row = {
            "name": name,
            "street_addr": street_addr,
            "city": city,
            "zipcode": zipcode,
            "phone": phone,
            "bed_count": bed_count,
            "web_url": web_url,
        }

        pprint(row)

        csv_writer.writerow(row)

    out_f.close()


if __name__ == "__main__":
    main()
