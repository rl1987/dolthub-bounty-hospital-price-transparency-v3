#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint
import re

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

def process_chargemaster(cms_id, url):
    resp = requests.get(url)
    print(resp.url)
    
    begins_at = resp.text.find(" Description of Item or Service")

    s_f = StringIO(resp.text[begins_at:])

    out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    csv_reader = csv.DictReader(s_f, delimiter="\t")
    
    for in_row in csv_reader:
        code = in_row.get(" CPT/HCPCS/ DRG Code ").strip()
        description = in_row.get(" Description of Item or Service ").strip()
        rev_code = in_row.get(" Revenue Code ").strip()
        quantity = in_row.get(" ERx Charge Quantity ").strip()
        gross = in_row.get(" Gross Charge ").replace("$", "").replace(",", "").strip()
        discounted = in_row.get(" Discounted Cash Price ").replace("$", "").replace(",", "").strip()

        if quantity == "N/A":
            quantity = ""

        out_row = {
            "cms_certification_num": cms_id,
            "code": code,
            "internal_revenue_code": "NONE",
            "units": quantity,
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": "NONE",
        }

        if gross != "N/A" and gross != "-":
            out_row["payer"] = "GROSS CHARGE"
            out_row["price"] = gross
            pprint(out_row)
            csv_writer.writerow(out_row)

        if discounted != "N/A" and discounted != "-":
            out_row["payer"] = "CASH PRICE"
            out_row["price"] = discounted
            pprint(out_row)
            csv_writer.writerow(out_row)

        payers = list(in_row.keys())[7:]
        for payer in payers:
            price = in_row.get(payer)
            price = price.replace("$", "").replace(",", "").strip()

            if payer == "De-identified Minimum Third-Party Payer Charges":
                payer = "MIN"

            if payer == "De-identified Maximum Third-Party Payer Charges":
                payer = "MAX"

            if price != "N/A" and price != "-":
                payer = payer.strip().replace("\n", " ")
                out_row["payer"] = payer
                out_row["price"] = price
                pprint(out_row)
                csv_writer.writerow(out_row)

    out_f.close()

def main():
    targets = {
        "231309": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/260806477_aspirus-ontonagon-hospital_standardcharges.json",
        "231318": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/383236977_aspirus-ironriver-hospital_standardcharges.json",
        "231319": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/381443361_aspirus-keweenaw-hospital_standardcharges.json",
        "231333": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/382908586_aspirus-ironwood-hospital_standardcharges.json",
        "520030": "https://www.aspirus.org/Uploads/Public/Documents/StandardCharges/2022/391138241_aspirus-wausau-hospital_standardcharges.json",
        "520033": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/390868982_aspirus-riverview-hospital_standardcharges.json",
        "520041": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/390806250_aspirus-divinesavior-hospital_standardcharges.JSON",
        "521324": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/390964813_aspirus-medford-hospital_standardcharges.json",
        "521350": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/390806429_aspirus-langlade-hospital_standardcharges.json",
        "521300": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/390985690_aspirus-eagleriver-hospital_standardcharges.JSON",
        "520091": "https://www.aspirus.org/Uploads/Public/Documents/Bill/StandardCharges/390873606_aspirus-howardyoung-medical-center_standardcharges.JSON"
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.aspirus.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
