#!/usr/bin/python3

import csv
from pprint import pprint
from io import BytesIO
import os

import requests
import xlrd

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
    filename = url.split("/")[-1]

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

# XXX: for some reason this cuts off the first digit of cms_certification_num on the first row
def scrape_hospital_data(cms_certification_num, xlsx_url, csv_writer):
    filename = download_chargemaster(xlsx_url)

    wb = xlrd.open_workbook(filename)
    ws = wb.sheet_by_index(0)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for i in range(ws.nrows):
        in_row = ws.row(i)
        if len(in_row) < 4:
            continue

        values = list(map(lambda cell: str(cell.value), in_row))

        if values[0] == "Charge Code":
            continue

        code = values[4]
        modifier = None
        if len(values) >= 6:
            modifier = values[5]

        if modifier is not None and modifier != "":
            code += "-" + modifier

        if code == "":
            code = "NONE"

        code = code.replace(".0", "")

        charge_code = values[0].replace(".0", "")
        description = values[1]
        price = values[2]

        if price == "":
            continue

        out_row = {
            "cms_certification_num": str(cms_certification_num),
            "payer": "GROSS CHARGES",
            "code": code,
            "internal_revenue_code": charge_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "price": price,
            "code_disambiguator": "NONE",
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

    out_f.close()

def main():
    targets = {
        "132002": "https://vhboise.com/wp-content/uploads/sites/24/2021/12/Boise-CDM-DECEMBER-2021.xls",
        "222043": "https://vhmass.com/wp-content/uploads/sites/35/2021/12/New-Bedford-CDM-DECEMBER-2021.xls",
        "222046": "https://vhwmasscentral.com/wp-content/uploads/sites/37/2021/12/Western-Massachusetts-Central-Campus-CDM-DECEMBER-2021.xls",
        "062014": "https://vhdenver.com/wp-content/uploads/sites/27/2021/12/North-Valley-Denver-LTAC-CDM-DECEMBER-2021.xls",
        "063035": "https://vrhdenver.com/wp-content/uploads/sites/20/2021/12/Denver-IRF-CDM-DECEMBER-2021.xls",
        "052033": "https://vhsacramento.com/wp-content/uploads/sites/34/2021/12/Sacramento-CDM-DECEMBER-2021.xls",
        "052047": "https://norcalrehab.com/wp-content/uploads/sites/30/2021/12/Redding-CDM-DECEMBER-2021.xls",
        "232019": "https://vhsemichigan.com/wp-content/uploads/sites/36/2021/12/Hospital-of-Southeastern-Michigan-Taylor-Campus-CDM-DECEMBER-2021.xls",
        "352004": "https://vhfargo.com/wp-content/uploads/sites/28/2021/12/Fargo-CDM-DECEMBER-2021.xls",
        "352005": "https://vhcentraldakotas.com/wp-content/uploads/sites/25/2021/12/Central-Dakotas-CDM-DECEMBER-2021.xls",
        "382004": "https://vshportland.com/wp-content/uploads/sites/39/2021/12/Portland-CDM-DECEMBER-2021.xls",
        "422005": "https://vhcharleston.com/wp-content/uploads/sites/26/2021/12/Charleston-CDM-DECEMBER-2021.xls",
        "362023": "https://vhmvalley.com/wp-content/uploads/sites/29/2021/12/Mahoning-Valley-Boardman-CDM-DECEMBER-2021.xls",
        "452060": "https://vhamarillo.com/wp-content/uploads/sites/2/2021/12/Amarillo-CDM-DECEMBER-2021.xls",
        #"452097": "https://vshdesoto.com/wp-content/uploads/sites/38/2021/12/Desoto_Rich-Facility-Proc-Master-220170.xlsx",
        "453096": "https://vrhamarillo.com/wp-content/uploads/sites/19/2021/12/Rehabilitation-Hospital-of-Amarillo-CDM-DECEMBER-2021.xls",
        "152028": "https://vhnwindiana.com/wp-content/uploads/sites/31/2021/12/Merrillville-CDM-DECEMBER-2021.xls",
        "492009": "https://vhrichmond.com/wp-content/uploads/sites/33/2021/12/Richmond-CDM-DECEMBER-2021.xls"
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
            'UPDATE `hospitals` SET `homepage_url` = "{}", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                xlsx_url.split('/wp-content/')[0], xlsx_url, csm_num
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
