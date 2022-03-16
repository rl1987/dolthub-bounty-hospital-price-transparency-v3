#!/usr/bin/python3

import csv
from io import StringIO
from pprint import pprint

import requests

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


def process_chargemaster(cms_certification_num, url):
    proxy_url = "http://lum-customer-c_cecd546c-zone-zone_isp_hca:ef171xfs3a8w@zproxy.lum-superproxy.io:22225"
    proxies = {"http": proxy_url, "https": proxy_url}

    resp = requests.get(url, proxies=proxies)
    print(resp.url)

    first_newline_at = resp.text.find("\n")

    s_f = StringIO(resp.text[first_newline_at + 1 :])

    csv_reader = csv.DictReader(s_f)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    for in_row in csv_reader:
        pprint(in_row)

        try:
            code_disambiguator = int(in_row.get("Procedure ID"))
        except:
            break

        code = in_row.get("HCPCS/CPT Code").strip()
        description = in_row.get("Description").strip()
        gross = in_row.get("Gross Charge")
        discounted = in_row.get("Discounted Cash Price (Gross Charges)")

        if code == "":
            code = "NONE"

        out_row = {
            "cms_certification_num": cms_certification_num,
            "payer": "CASH PRICE",
            "code": code,
            "internal_revenue_code": "NONE",
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "price": discounted,
            "code_disambiguator": code_disambiguator,
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

        out_row["payer"] = "GROSS CHARGE"
        out_row["price"] = gross

        pprint(out_row)
        csv_writer.writerow(out_row)

    out_f.close()


def main():
    targets = {
        "670103": "https://core.secure.ehc.com/src/util/detail-price-list/46-4027347_medical-city-alliance_standardcharges.csv",
        "450087": "https://core.secure.ehc.com/src/util/detail-price-list/62-1682205_medical-city-north-hills_standardcharges.csv",
        "450203": "https://core.secure.ehc.com/src/util/detail-price-list/822073410_medical-city-weatherford_standardcharges.csv",
        "450403": "https://core.secure.ehc.com/src/util/detail-price-list/62-1682207_medical-city-mckinney_standardcharges.csv",
        "450634": "https://core.secure.ehc.com/src/util/detail-price-list/62-1682213_medical-city-denton_standardcharges.csv",
        "450647": "https://core.secure.ehc.com/src/util/detail-price-list/62-1682198_medical-city-dallas_standardcharges.csv",
        "450651": "https://core.secure.ehc.com/src/util/detail-price-list/62-1682203_medical-city-plano_standardcharges.csv",
        "450669": "https://core.secure.ehc.com/src/util/detail-price-list/62-1682210_medical-city-lewisville_standardcharges.csv",
        "450672": "https://core.secure.ehc.com/src/util/detail-price-list/62-1682202_medical-city-fort-worth_standardcharges.csv",
        "450675": "https://core.secure.ehc.com/src/util/detail-price-list/62-1682201_medical-city-arlington_standardcharges.csv",
        "450822": "https://core.secure.ehc.com/src/util/detail-price-list/62-1650582_medical-city-las-colinas_standardcharges.csv",
    }

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

# update prices set internal_revenue_code = code_disambiguator, code_disambiguator = internal_revenue_code where cms_certification_num in (select cms_certification_num from hospitals where homepage_url = 'https://medicalcityhealthcare.com/home/');


if __name__ == "__main__":
    main()
