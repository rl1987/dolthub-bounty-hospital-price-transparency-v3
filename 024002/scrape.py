#!/usr/bin/python3

import csv
from pprint import pprint

import tabula

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
    cms_certification_num = "024002"

    dfs = tabula.read_pdf("https://dhss.alaska.gov/API/Documents/Acute-Rate-Matrix.pdf")
    df = dfs[0]

    n = 1

    out_f = open("024002.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    for row in df.iterrows():
        description = row[1]['Description']
        price = row[1]['Charge']

        if price.startswith('$'):
            price = price.replace("$", "")
        else:
            continue

        price = price.strip()
        description = description.strip()

        out_row = {
            "cms_certification_num": cms_certification_num,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": str(n),
            "price": price,
            "payer": "GROSS",
            "code": "NONE",
            "internal_revenue_code": "NONE",
        }

        pprint(out_row)

        csv_writer.writerow(out_row)

        n += 1

    out_f.close()

if __name__ == "__main__":
    main()
