#!/usr/bin/python3

import csv
from pprint import pprint
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

def process_chargemaster(cms_id, url):
    resp = requests.get(url)
    print(resp.url)

    s_f = StringIO(resp.text)

    out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    csv_reader = csv.DictReader(s_f)

    for in_row in csv_reader:
        out_row = {
            "cms_certification_num": cms_id,
            "payer": "GROSS",
            "code": in_row.get("CPT Code").strip(),
            "internal_revenue_code": in_row.get("Revenue Code").strip(),
            "units": "",
            "description": in_row.get("Code Description").strip(),
            "inpatient_outpatient": "UNSPECIFIED",
            "price": in_row.get("Charge").strip(),
            "code_disambiguator": "NONE",
        }

        pprint(out_row)

        csv_writer.writerow(out_row)

    out_f.close()

def main():
    targets = {
        "160028": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_CB.csv",
        "161304": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_Corning.csv",
        "161309": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_MissouriValley.csv",
        "280009": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_GoodSam.csv",
        "280020": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_St.Elizabeth.csv",
        "280023": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_St.Francis.csv",
        "280060": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_07_35_34PM.csv",
        "280081": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_Immanuel.csv",
        "280105": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_Midlands.csv",
        "280128": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_NebraskaHeart.csv",
        "280130": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_Lakeside.csv",
        "281323": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_Schuyler.csv",
        "281342": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_St.Mary.csv",
        "281346": "https://www.chihealth.com/content/dam/chi-health/website/documents/cost-estimates/Charges_CSVreport_11_Jan_2021_Plainview.csv",
    }

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

if __name__ == "__main__":
    main()

