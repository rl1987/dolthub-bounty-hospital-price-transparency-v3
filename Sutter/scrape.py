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
    resp = requests.get(url)
    print(resp.url)

    first_newline_at = resp.text.index("\n")

    s_f = StringIO(resp.text[first_newline_at+1:])

    csv_reader = csv.DictReader(s_f)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    disamb = dict()

    for in_row in csv_reader:
        payers = list(in_row.keys())[6:]

        code = in_row.get("CPT")
        if code == "":
            code = "NONE"

        code_disambiguator = disamb.get(code)
        if code_disambiguator is None:
            code_disambiguator = 1
        else:
            code_disambiguator += 1

        rev_code = in_row.get("REVENUE_CODE")
        if rev_code == "":
            rev_code = "NONE"

        disamb[code] = code_disambiguator

        inpatient_outpatient = in_row.get("SERVICE_SETTING")
        description = in_row.get("DESCRIPTION")

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "code_disambiguator": code_disambiguator
        }

        for payer in payers:
            price = in_row.get(payer)

            if price == "":
                continue

            if payer == "Gross Charge":
                payer = "GROSS CHARGE"
            elif payer == "Discounted Cash Price":
                payer = "CASH PRICE"
            elif payer == "Minimum Negotiated Price":
                payer = "MIN"
            elif payer == "Maximum Negotiated Price":
                payer = "MAX"

            price = price.replace("$", "").replace(",", "").strip()

            out_row['price'] = price
            out_row['payer'] = payer

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()

def main():
    targets = {
        "050014": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1447494323_SUTTER-AMADOR-HOSPITAL_standardcharges.csv",
        "050101": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1366686248_SUTTER-SOLANO-MEDICAL-CENTER_standardcharges.csv",
        "050108": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1811946734_SUTTER-MEDICAL-CENTER-SACRAMENTO_standardcharges.csv",
        "050291": "https://www.sutterhealth.org/pdf/chargemaster/940562680-1740413798_SUTTER-SANTA-ROSA-REGIONAL-HOSPITAL_standardcharges.csv",
        "050309": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1356390264_SUTTER-ROSEVILLE-MEDICAL-CENTER_standardcharges.csv",
        "050313": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1821442864_SUTTER-TRACY-COMMUNITY-HOSPITAL_standardcharges.csv",
        "050417": "https://www.sutterhealth.org/pdf/chargemaster/942988520-1700960267_SUTTER-COAST-HOSPITAL_standardcharges.csv",
        "050498": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1194774299_SUTTER-AUBURN-FAITH-HOSPITAL_standardcharges.csv",
        "050523": "https://www.sutterhealth.org/pdf/chargemaster/940562680-1467808659_SUTTER-DELTA-MEDICAL-CENTER_standardcharges.csv",
        "050537": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1770532608_SUTTER-DAVIS-HOSPITAL_standardcharges.csv",
        "050714": "https://www.sutterhealth.org/pdf/chargemaster/940562680-1689035628_SUTTER-MATERNITY-SURGERY-CENTER-OF-SANTA-CRUZ_standardcharges.csv",
        "050766": "https://www.sutterhealth.org/pdf/chargemaster/352182617-1336333954_SUTTER-NORTH-VALLEY-SURGICAL-HOSPITAL_standardcharges.csv",
        "051329": "https://www.sutterhealth.org/pdf/chargemaster/940562680-1952634008_SUTTER-LAKESIDE-HOSPITAL_standardcharges.csv",
        "054096": "https://www.sutterhealth.org/pdf/chargemaster/941156621-1952350944_SUTTER-CENTER-FOR-PSYCHIATRY_standardcharges.csv"
    }

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

if __name__ == "__main__":
    main()
