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

def scrape_hospital_data(cms_certification_num, xlsx_url, csv_writer):
    resp = requests.get(xlsx_url)
    print(resp)
    print(resp.url)

    b_f = BytesIO(resp.content)

    wb = openpyxl.load_workbook(b_f)
    ws = wb.active
 
    input_fieldnames = None
    payers = None

    code_disambiguator = 0

    for in_row in ws.rows:
        values = list(map(lambda cell: cell.value, in_row))
        if values[0] == "Item/Service Description":
            input_fieldnames = values
            payers = values[4:]
            continue

        code_disambiguator += 1

        in_row_dict = dict(zip(input_fieldnames, values))

        pprint(in_row_dict)

        description = in_row_dict.get("Item/Service Description")
        code = "NONE"
        
        rev_code = in_row_dict.get("Billing Code")

        for payer in payers:
            price = in_row_dict.get(payer)
            if price == "N/A":
                continue

            payer = payer.replace("\n", " ")

            if payer == "Discounted Cash Price":
                payer = "CASH PRICE"
            elif payer == "Minimum Negotiated Charge":
                payer = "MIN"
            elif payer == "Maximum Negotiated Charge":
                payer = "MAX"
            else:
                payer = payer.split(" Negotiated")[0]

            out_row = {
                "cms_certification_num": cms_certification_num,
                "code": code,
                "internal_revenue_code": rev_code,
                "units": "",
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
        "012007": "https://nolandhospitals.com/wp-content/uploads/2020/12/473388048_Noland-Hospital-Montgomery_standardcharges.xlsx",
        "012009": "https://nolandhospitals.com/wp-content/uploads/2020/12/473385197_Noland-Hospital-Birmingham_standardcharges.xlsx",
        "012010": "https://nolandhospitals.com/wp-content/uploads/2020/12/472491675_Noland-Hospital-Dothan_standardcharges.xlsx",
        "012011": "https://nolandhospitals.com/wp-content/uploads/2020/12/472862505_Noland-Hospital-Anniston_standardcharges.xlsx",
        "012012": "https://nolandhospitals.com/wp-content/uploads/2020/12/472847958_Noland-Hospital-Tuscaloosa_standardcharges.xlsx"
    }

    for csm_num in targets.keys():
        out_f = open("{}.csv".format(csm_num), "w", encoding="utf-8")

        csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
        csv_writer.writeheader()

        xlsx_url = targets[csm_num]

        scrape_hospital_data(csm_num, xlsx_url, csv_writer)

        out_f.close()

if __name__ == "__main__":
    main()
