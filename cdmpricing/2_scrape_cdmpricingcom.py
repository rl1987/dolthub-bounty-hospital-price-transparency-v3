#!/usr/bin/python3 

import csv
from pprint import pprint

import requests

FIELDNAMES = [
    #"cms_certification_num",
    "cdm_id",
    "hospital_name",
    "payer",
    "code",
    "internal_revenue_code",
    "units",
    "description",
    "inpatient_outpatient",
    "price",
    "code_disambiguator",
]

def scrape_cdm(cdm_id):
    out_f = open(cdm_id + ".csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    resp0 = requests.get("https://apim.services.craneware.com/api-pricing-transparency/api/public/{}/metadata/name".format(cdm_id))
    print(resp0.url)
    
    hospital_name = resp0.json().get("name").strip()

    page = 0
    limit = 50

    while True:
        params = {
            'page': page,
            'limit': limit,
            'search': '',
            'codeType': '',
        }

        resp = requests.get("https://apim.services.craneware.com/api-pricing-transparency/api/public/{}/charges/standardCharges".format(cdm_id), params=params)
        print(resp.url)

        items = resp.json().get("response")
        
        for item_dict in items:
            if item_dict.get("cranewareShoppable") != "":
                inpatient_outpatient = "OUTPATIENT"
            else:
                inpatient_outpatient = "INPATIENT"

            row = {
                "cdm_id": cdm_id,
                "hospital_name": hospital_name,
                "code": item_dict.get("code"),
                "internal_revenue_code": "NONE",
                "units": "",
                "description": item_dict.get("description"),
                "inpatient_outpatient": inpatient_outpatient,
                "code_disambiguator": item_dict.get("id"),
            }

            gross = item_dict.get("grossCharge")
            if gross != "" and gross != "-":
                row['payer'] = "GROSS CHARGE"
                row['price'] = gross
                pprint(row)
                csv_writer.writerow(row)

            discounted = item_dict.get("selfPay")
            if discounted != "" and discounted != "-":
                row['payer'] = "CASH PRICE"
                row['price'] = discounted
                pprint(row)
                csv_writer.writerow(row)

            for payer_dict in item_dict.get("payors"):
                price = payer_dict.get("avgAllowable")
                if price == "":
                    continue

                payer = payer_dict.get("name")

                row['payer'] = payer
                row['price'] = price
                pprint(row)
                csv_writer.writerow(row)

        if len(items) < limit:
            break

        page += 1
        
    out_f.close()

def main():
    in_f = open("cdm_ids.txt", "r")

    for cdm_id in in_f.read().strip().split("\n"):
        scrape_cdm(cdm_id)

    in_f.close()

if __name__ == "__main__":
    main()

