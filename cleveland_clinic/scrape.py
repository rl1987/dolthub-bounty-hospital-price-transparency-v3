#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint
import os

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

def download_chargemaster(url):
    filename = url.split("/")[-1]

    if os.path.isfile(filename):
        print("{} already downloaded".format(filename))
        return filename

    print("Downloading: {} -> {}".format(url, filename))
    
    # Based on: https://stackoverflow.com/a/16696317
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return filename

def process_chargemaster(cms_id, url):
    filename = download_chargemaster(url)

    out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    in_f = open(filename, "r", encoding="cp1252")

    csv_reader = csv.DictReader(in_f)

    #for in_row in csv_reader:
    #    code = in_row.get("Code").split(' ')[-1]
    #    internal_revenue_code = in_row.get("Rev Code").split(" - ")[0]
    #    description = in_row.get("Procedure Description")
    #    code_disambiguator = in_row.get("Procedure")

    in_f.close()
    out_f.close()

def main():
    targets = {
        "360180":"https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340714585_cleveland-clinic-main-campus_standardcharges.csv",
        "363038": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/474442902_avon-hospital_standardcharges.csv",
        "100289": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/650844880_cleveland-clinic-florida-weston-hospital_standardcharges.csv",
        "363304": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340714570_cleveland-clinic-childrens-hospital-for-rehabilitation_standardcharges.csv",
        "360082": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340714593_euclid-hospital_standardcharges.csv",
        "360077": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340714618_fairview-hospital_standardcharges.csv",
        "360230": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340714593_hillcrest-hospital_standardcharges.csv",
        #"100105": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/592496294_indian-river-hospital_standardcharges.xlsx",
        "361303": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340718390_lodi-hospital_standardcharges.csv",
        "360087": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340714684_lutheran-hospital_standardcharges.csv",
        "360143": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340714458_marymount-hospital_standardcharges.csv",
        "360091": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340733166_medina-hospital_standardcharges.csv",
        "360144": "https://my.clevelandclinic.org/-/scassets/files/org/patients-visitors/hospital-standard-charge-files/340714593_south-pointe-hospital_standardcharges.csv",
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://my.clevelandclinic.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
