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


def main():
    cms_certification_num = "061320"

    resp = requests.get(
        "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbGVHGUNNISONCO&type=CDMWithoutLabel"
    )
    print(resp.url)

    csv_reader = csv.reader(StringIO(resp.text))

    out_f = open("061320.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    next(csv_reader)
    next(csv_reader)
    next(csv_reader)

    input_fieldnames = next(csv_reader)

    payers = input_fieldnames[8:]

    disamb = dict()

    for in_row in csv_reader:
        in_row_dict = dict(zip(input_fieldnames, in_row))

        if len(in_row_dict) == 0:
            break

        pprint(in_row_dict)

        code = in_row_dict.get("CPT HCPCS Code")
        if code == "":
            code = "NONE"

        internal_revenue_code = in_row_dict.get("Revenue Code")
        if internal_revenue_code == "":
            internal_revenue_code = "NONE"

        code_disambiguator = disamb.get(code)
        if code_disambiguator is None:
            code_disambiguator = 1
        else:
            code_disambiguator += 1

        disamb[code] = code_disambiguator

        units = in_row_dict.get("Rx Unit Multiplier")
        if units == "NA":
            units = ""

        description = in_row_dict.get("Procedure Description")

        price_tier = in_row_dict.get("Price Tier")
        inpatient_outpatient = "UNSPECIFIED"
        if price_tier == "Inpatient":
            inpatient_outpatient = "INPATIENT"
        elif price_tier == "Outpatient":
            inpatient_outpatient = "OUTPATIENT"

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": internal_revenue_code,
            "units": units,
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "code_disambiguator": code_disambiguator,
        }

        for payer in payers:
            price = in_row_dict.get(payer)

            if price == "" or price is None:
                continue

            if "." in price and len(price.split(":")[-1]) == 4:
                price = price[:-2]

            if payer == "Gross Charge":
                payer = "GROSS CHARGE"
            elif payer == "Discounted Cash Price":
                payer = "CASH PRICE"
            elif payer == "De-identified minimum negotiated charge":
                payer = "MIN"
            elif payer == "De-identified maximum negotiated charge":
                payer = "MAX"

            out_row["payer"] = payer
            out_row["price"] = price

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()


if __name__ == "__main__":
    main()
