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

    for in_row in ws.rows:
        if len(in_row) < 3:
            continue

        if in_row[0].value == "Procedure" or str(in_row[0].value).startswith("Update"):
            continue

        code_disambiguator = "NONE"

        if len(in_row) == 5:
            code = in_row[1].value

            if code is None or code == "":
                code = "NONE"

            if type(code) == float or type(code) == int:
                code = str(int(code))

            code = code.strip()
        else:
            code = "NONE"

        if len(in_row) == 5:
            description = in_row[2].value
        else:
            description = in_row[1].value

        description = description.strip()

        price = in_row[-1].value

        out_row = {
            "cms_certification_num": cms_certification_num,
            "payer": "GROSS CHARGES",
            "code": code,
            "internal_revenue_code": "NONE",
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "price": price,
            "code_disambiguator": code_disambiguator,
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

    b_f.close()


def main():
    targets = {
        "012006": "https://www.infirmaryhealth.org/documents/price%20transparency%20files/Ltac-Charge-Master.xlsx",
        "010113": "https://www.infirmaryhealth.org/documents/Price%20Transparency%20Files/Mobile-Infirmary-Charge-Master.xlsx",
        "010129": "https://www.infirmaryhealth.org/documents/price%20transparency%20files/North-Baldwin-Infirmary-Charge-Master.xlsx",
        "010100": "https://www.infirmaryhealth.org/documents/price%20transparency%20files/Thomas-Hospital-Charge-Master.xlsx",
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
            'UPDATE `hospitals` SET `homepage_url` = "https://www.infirmaryhealth.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                xlsx_url, csm_num
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
