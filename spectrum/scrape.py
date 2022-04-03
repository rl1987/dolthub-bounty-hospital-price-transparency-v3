#!/usr/bin/python3

import csv
from pprint import pprint
from io import BytesIO
import uuid

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


def fix_price(price_str):
    price_str = price_str.replace("$", "").replace(",", "").strip()

    if "." in price_str and len(price_str.split(".")[-1]) > 2:
        price_str = price_str.split(".")[0] + "." + price_str.split(".")[-1][:2]

    return price_str


def scrape_hospital_data(cms_certification_num, xlsx_url, csv_writer):
    resp = requests.get(xlsx_url)
    print(resp)
    print(resp.url)

    b_f = BytesIO(resp.content)

    wb = openpyxl.load_workbook(b_f)
    ws = wb.active

    input_fieldnames = None
    payers = None

    for in_row in ws.rows:
        values = list(map(lambda cell: cell.value, in_row))

        if values[0] == "Procedure Code":
            input_fieldnames = values
            continue

        if input_fieldnames is None:
            continue

        in_row_dict = dict(zip(input_fieldnames, values))
        pprint(in_row_dict)

        code_disambiguator = in_row_dict.get("Procedure Code")

        description = in_row_dict.get("Procedure Description")

        code = in_row_dict.get("CPT or HCPCS Code")

        if code == "" or code is None:
            code = "NONE"

        modifier = in_row_dict.get("Modifier")
        if modifier is not None and modifier != "":
            code += "-" + modifier

        rev_code = in_row_dict.get("REV Code")
        if rev_code is None or rev_code == "":
            rev_code = "NONE"

        inpatient_outpatient = "UNSPECIFIED"
        
        billing_category = in_row_dict.get("Billing Category")
        if billing_category is not None and "Inpatient" in billing_category:
            inpatient_outpatient = "INPATIENT"

        gross = in_row_dict.get("Charge Amount")
        if gross is None:
            continue

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "payer": "GROSS CHARGE",
            "price": gross,
            "code_disambiguator": code_disambiguator
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

    b_f.close()


def main():
    targets = {
        "230038": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/blt8e2ea76e3ebd3d96/Spectrum-Health-Butterworth-Hospital-CDM-File-Effective-01-01-21.xlsx",
        "230078": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/blt27db4f7e9b9e3c93/Spectrum-Health-Lakeland-Hospitals-CDM-File-Effective-01-01-22.xlsx",
        "230021": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/blt27db4f7e9b9e3c93/Spectrum-Health-Lakeland-Hospitals-CDM-File-Effective-01-01-22.xlsx",
        "231317": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/bltaa681a96299b6b54/Spectrum-Health-Hospitals-Regional-Hospitals-CDM-File-Effective-01-01-21.xlsx",
        "231323": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/bltaa681a96299b6b54/Spectrum-Health-Hospitals-Regional-Hospitals-CDM-File-Effective-01-01-21.xlsx",
        "231338": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/bltaa681a96299b6b54/Spectrum-Health-Hospitals-Regional-Hospitals-CDM-File-Effective-01-01-21.xlsx",
        "231339": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/bltaa681a96299b6b54/Spectrum-Health-Hospitals-Regional-Hospitals-CDM-File-Effective-01-01-21.xlsx",
        "230035": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/bltaa681a96299b6b54/Spectrum-Health-Hospitals-Regional-Hospitals-CDM-File-Effective-01-01-21.xlsx",
        "230093": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/bltaa681a96299b6b54/Spectrum-Health-Hospitals-Regional-Hospitals-CDM-File-Effective-01-01-21.xlsx",
        "230110": "https://assets.contentstack.io/v3/assets/blt7b132cfc09cf5e18/bltaa681a96299b6b54/Spectrum-Health-Hospitals-Regional-Hospitals-CDM-File-Effective-01-01-21.xlsx",
    }

    h_f = open("hospitals.sql", "w")

    for csm_num in targets.keys():
        out_f = open("{}.csv".format(csm_num), "w", encoding="utf-8")

        csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
        csv_writer.writeheader()

        xlsx_url = targets[csm_num]

        scrape_hospital_data(csm_num, xlsx_url, csv_writer)

        out_f.close()

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.spectrumhealth.org", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                xlsx_url, csm_num
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
