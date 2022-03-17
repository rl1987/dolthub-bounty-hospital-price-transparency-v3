#!/usr/bin/python3

import csv
from pprint import pprint
from io import BytesIO

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
        if values[0] == "CLEVELAND CLINIC INDIAN RIVER HOSPITAL - Price Transparency":
            continue

        if values[0] == "Site":
            input_fieldnames = values
            payers = values[6:]
            continue

        in_row_dict = dict(zip(input_fieldnames, values))

        pprint(in_row_dict)

        description = in_row_dict.get("CDM_Svc_Descr")
        code = in_row_dict.get("HCPC/Cpt_Cd")
        if code == "N/A":
            code = "NONE"
        rev_code = in_row_dict.get("Rev_Cd")
        code_disambiguator = "NONE"
        units = in_row_dict.get("Quantity/Units")

        for payer in payers:
            price = in_row_dict.get(payer)
            if price == "N/A" or price == "Inpt Medicare Pricing":
                continue

            price = str(price)
            price = fix_price(price)

            if payer == "Hopsital_Cdm_Chg":
                payer = "GROSS CHARGE"
            elif payer == "Self_Pay_Chg":
                payer = "CASH PRICE"
            elif payer == "Minimum_Negotiated_Chg":
                payer = "MIN"
            elif payer == "Maximum_Negotiated_Chg":
                payer = "MAX"

            out_row = {
                "cms_certification_num": cms_certification_num,
                "code": code,
                "internal_revenue_code": rev_code,
                "units": units,
                "description": description,
                "inpatient_outpatient": "UNSPECIFIED",
                "code_disambiguator": code_disambiguator,
                "payer": payer,
                "price": price,
            }

            pprint(out_row)
            csv_writer.writerow(out_row)

    b_f.close()


def main():
    targets = {
        "100105": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/592496294_indian-river-hospital_standardcharges.xlsx",
    }

    for csm_num in targets.keys():
        out_f = open("out_{}.csv".format(csm_num), "w", encoding="utf-8")

        csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
        csv_writer.writeheader()

        xlsx_url = targets[csm_num]

        scrape_hospital_data(csm_num, xlsx_url, csv_writer)

        out_f.close()


if __name__ == "__main__":
    main()
