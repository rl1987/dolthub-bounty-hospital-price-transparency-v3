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
    headers = {
        'authority': 'amgihm.com',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://amgihm.com/locations/north-alabama/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    resp = requests.get(xlsx_url, headers=headers)
    print(resp)
    print(resp.url)

    b_f = BytesIO(resp.content)

    wb = openpyxl.load_workbook(b_f)
    ws = wb.active
    
    for in_row in ws.rows:
        if len(in_row) < 4:
            continue

        internal_no = in_row[0].value
        description = in_row[1].value
        code = in_row[2].value
        price = in_row[3].value

        if price is None or price == "Standard Amount":
            continue

        out_row = {
            "cms_certification_num": cms_certification_num,
            "payer": "LIST PRICE",
            "code": code,
            "internal_revenue_code": internal_no,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "price": price,
            "code_disambiguator": "NONE",
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

    b_f.close()

def main():
    targets = {
        "192037" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Houma-Price-Transparency-01-2022.xlsx",
        "193097" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Covington-Rehab-Price-Transparency-01-2022.xlsx",
        "193093" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Lafayette-Rehab-Price-Transparency-01-2022.xlsx",
        "192041" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Zachary-Price-Transparency-01-2022.xlsx",
        "292007" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Las-Vegas-Price-Transparency-01-2022.xlsx",
        "192029" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Lafayette-Price-Transparency-01-2022.xlsx",
        "192037" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Houma-Price-Transparency-01-2022.xlsx",
        "372005" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Oklahoma-City-Price-Transparency-01-2022.xlsx",
        "152025" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Central-Indiana-Price-Transparency-01-2022.xlsx",
        "322003" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/Albuquerque-Price-Transparency-01-2022.xlsx",
        "012014" : "https://28g1xh366uy0x9ort41hns72-wpengine.netdna-ssl.com/wp-content/uploads/2021/12/North-Alabama-Price-Transparency-01-2022.xlsx",
    }

    out_f = open("amg.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    for csm_num in targets.keys():
        xlsx_url = targets[csm_num]

        scrape_hospital_data(csm_num, xlsx_url, csv_writer)

    out_f.close()

if __name__ == "__main__":
    main()
