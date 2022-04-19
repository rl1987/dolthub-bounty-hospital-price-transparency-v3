#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint

import requests
import openpyxl

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
    resp = requests.get(url)
    print(resp.url)

    csv_reader = csv.DictReader(StringIO(resp.text), delimiter="|")

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for in_row in csv_reader:
        payers = in_row.get("Insurance Plan(s)").split(", ")

        code = in_row.get("CPT / HCPCS Code")
        if code == "" or code is None:
            code = "NONE"
        else:
            code = code.split(" ")[-1]

        code_disambiguator = in_row.get("Procedure")

        description = in_row.get("Procedure Description")

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": "NONE",
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": code_disambiguator,
        }

        gross = in_row.get("Charge")
        if gross != "" and not "-" in gross and gross != "#N/A":
            out_row["payer"] = "GROSS CHARGE"
            out_row["price"] = gross.strip().replace(",", "")
            pprint(out_row)
            csv_writer.writerow(out_row)

        discounted = in_row.get("Cash Discount Expected Reimbursement")
        if discounted != "" and not "-" in discounted and discounted != "#N/A":
            out_row["payer"] = "CASH PRICE"
            out_row["price"] = discounted.strip().replace(",", "")
            pprint(out_row)
            csv_writer.writerow(out_row)

        min_price = in_row.get("All Plans Minimum Expected Reimbursement")
        if min_price != "" and not "-" in min_price:
            out_row["payer"] = "MIN"
            out_row["price"] = min_price.strip().replace(",", "")
            pprint(out_row)
            csv_writer.writerow(out_row)

        max_price = in_row.get("All Plans Maximum Expected Reimbursement")
        if min_price != "" and not "-" in min_price:
            out_row["payer"] = "MAX"
            out_row["price"] = max_price.strip().replace(",", "")
            pprint(out_row)
            csv_writer.writerow(out_row)

        plan_price = in_row.get("Plan Expected Reimbursement")
        if plan_price != "" and not "-" in plan_price:
            for payer in payers:
                out_row["payer"] = payer
                out_row["price"] = plan_price.strip().replace(",", "")
                pprint(out_row)
                csv_writer.writerow(out_row)

    out_f.close()


def main():
    targets = {
        "501329": "https://app.peacehealth.org/FileRepository/Financial/StandardCharges/UGMC/37-1715059_United_General_Medical_Center_StandardCharges.csv",
        "501340": "https://app.peacehealth.org/FileRepository/Financial/StandardCharges/PIMC/38-3868360_Peace_Island_Medical_Center_StandardCharges.csv",
        "381301": "https://app.peacehealth.org/FileRepository/Financial/StandardCharges/CGMC/93-1279544_Cottage_Grove_Community_Medical_Center_StandardCharges.csv",
        "500041": "https://app.peacehealth.org/FileRepository/Financial/StandardCharges/STJN/91-0564987_St_John_Medical_Center_StandardCharges.csv",
        "500050": "https://app.peacehealth.org/FileRepository/Financial/StandardCharges/SWMC/91-6068143_Southwest_Medical_Center_StandardCharges.csv",
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.peacehealth.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
