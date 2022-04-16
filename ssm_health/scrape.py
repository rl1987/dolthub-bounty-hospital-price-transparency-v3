#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint
import re
import os
import json

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

def download_chargemaster(url):
    resp0 = requests.head(url)
    url = resp0.headers['Location']
    resp1 = requests.head(url)

    filename = resp1.headers['Content-Disposition'].split("=")[-1]

    if os.path.isfile(filename):
        print("{} already downloaded".format(filename))
        return filename

    print("Downloading: {} -> {}".format(url, filename))

    # Based on: https://stackoverflow.com/a/16696317
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return filename

def fix_price(price_str):
    return price_str.replace("$", "").replace(",", "")

def process_chargemaster(cms_id, url):
    filename = download_chargemaster(url)

    in_f = open(filename, "r", encoding="utf-8")

    json_dict = json.load(in_f)
    json_arr = json_dict.get("MRF")

    out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for in_row in json_arr:
        pprint(in_row)
        code = in_row.get("code")
        description = in_row.get("code_desc")
        rev_code = in_row.get("rev_code")
        quantity = in_row.get("implied_quantity")
        if quantity == "N/A":
            quantity = ""

        modifier = in_row.get("modifier")

        if code != "" and modifier != "":
            code += "-" + modifier

        if code == "" or code is None:
            code = "NONE"

        if rev_code == "" or rev_code is None:
            rev_code = "NONE"
 
        code = code.replace("'", "")

        inpatient_outpatient = "UNSPECIFIED"
        area = in_row.get("area")
        if area == "IP":
            inpatient_outpatient = "INPATIENT"
        elif area == "OP":
            inpatient_outpatient = "OUTPATIENT"

        out_row = {
            "cms_certification_num": cms_id,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": quantity,
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "code_disambiguator": "NONE",
        }

        gross = in_row.get("standard_gross_charge")
        if gross != "N/A":
            out_row["payer"] = "GROSS CHARGE"
            out_row["price"] = fix_price(gross)
            pprint(out_row)
            csv_writer.writerow(out_row)

        discounted = in_row.get("discounted_cash_price")
        if discounted != "N/A":
            out_row["payer"] = "CASH PRICE"
            out_row["price"] = fix_price(discounted)
            pprint(out_row)
            csv_writer.writerow(out_row)

        min_price = in_row.get("minimum_negotiated")
        if min_price != "N/A":
            out_row["payer"] = "MIN"
            out_row["price"] = fix_price(min_price)
            pprint(out_row)
            csv_writer.writerow(out_row)

        max_price = in_row.get("maximum_negotiated")
        if max_price != "N/A":
            out_row["payer"] = "MAX"
            out_row["price"] = fix_price(max_price)
            pprint(out_row)
            csv_writer.writerow(out_row)

        plan = in_row.get("contract_name")
        plan_price = in_row.get("payer_specific_negotiated_rate")
        if plan_price != "N/A":
            out_row["payer"] = plan
            out_row["price"] = fix_price(plan_price)
            pprint(out_row)
            csv_writer.writerow(out_row)

    in_f.close()
    out_f.close()

def main():
    targets = {
        "260081": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-clare-fenton",
        "260091": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-marys-st-louis",
        "260104": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/depaul",
        "260105": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/saint-louis-university-hospital",
        "260200": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-joseph-lake-saint-louis",
        "140034": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-marys-centralia",
        "260005": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-joseph-st-charles",
        "260011": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-marys-jefferson-city",
        "370037": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-anthony-okc",
        "370149": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-anthony-shawnee",
        "520057": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-clare-baraboo",
        "520083": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-marys-madison",
        "520208": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/st-marys-janesville",
        "521327": "https://ssmhealth.pt.panaceainc.com/MRFDownload/ssmhealth/waupun-memorial"
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.ssmhealth.com/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
