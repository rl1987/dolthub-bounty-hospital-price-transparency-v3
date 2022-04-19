#!/usr/bin/python3

import csv
from pprint import pprint
import os
import zipfile

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


def download_chargemaster(url):
    filename = url.split("/")[-1]

    # if os.path.isfile(filename):
    #    print("{} already downloaded".format(filename))
    #    return filename

    print("Downloading: {} -> {}".format(url, filename))

    # Based on: https://stackoverflow.com/a/16696317
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    if filename.endswith(".zip"):
        z_f = zipfile.ZipFile(filename)
        for n in z_f.namelist():
            if n.endswith("/"):
                continue

            if (
                "Procedure Master" in n.split("/")[-1]
                or "chrg mstr" in n.split("/")[-1]
                or "CDM" in n.split("/")[-1]
            ) and n.endswith(".xlsx"):
                print("Extracting {} from {}".format(n, filename))
                filename = n.split("/")[-1]
                filename = z_f.extract(n, filename)
                break

        z_f.close()

    return filename


def scrape_hospital_data(cms_certification_num, xlsx_url, csv_writer):
    filename = download_chargemaster(xlsx_url)

    wb = openpyxl.load_workbook(filename)
    ws = wb.active

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    keys = None

    for in_row in ws:
        if len(in_row) < 4:
            continue

        values = list(map(lambda cell: str(cell.value), in_row))

        if (
            values[0] == "Procedure Number"
            or values[0] == "Charge Code"
            or values[0] == "CHARGE CODE"
        ):
            keys = values
            continue

        if keys is None:
            continue

        in_row_dict = dict(zip(keys, values))
        pprint(in_row_dict)

        code_disambiguator = in_row_dict.get("Procedure Number")
        if code_disambiguator is None:
            code_disambiguator = in_row_dict.get("Charge Code")
        if code_disambiguator is None:
            code_disambiguator = in_row_dict.get("CHARGE CODE")

        if code_disambiguator is None:
            continue

        code = in_row_dict.get("CPT Code")
        if code is None:
            code = in_row_dict.get("CPT CODE")

        modifier = in_row_dict.get("Modifier")
        if modifier is None:
            modifier = in_row_dict.get("MODIFIER")

        if code is not None and modifier is not None:
            code += "-" + modifier

        if code is None or code == "-":
            code = "NONE"

        modifier1 = in_row_dict.get("Modifier 1")
        rev_code = in_row_dict.get("Revenue Code")

        if rev_code is not None and modifier1 is not None and modifier1 != "":
            rev_code += "-" + modifier1

        if rev_code is None:
            rev_code = in_row_dict.get("UB Code")

        if rev_code is None:
            rev_code = in_row_dict.get("UB CODE")

        if rev_code is None:
            rev_code = "NONE"

        description = in_row_dict.get("Description")
        if description is None:
            description = in_row_dict.get("DECRIPTION")

        price = in_row_dict.get("Standard Amount")

        if price is None:
            price = in_row_dict.get("Amount")

        if price is None:
            price = in_row_dict.get("AMOUNT")

        if price is None or "=SUM" in price or price == "None":
            continue

        out_row = {
            "cms_certification_num": cms_certification_num,
            "payer": "GROSS CHARGES",
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "price": price,
            "code_disambiguator": code_disambiguator,
        }

        pprint(out_row)
        csv_writer.writerow(out_row)

    out_f.close()


def main():
    targets = {
        "272001": "https://achm.ernesthealth.com/wp-content/uploads/2022/01/Advanced-Care-Montana-Facility-Procedure-Master-120050.xlsx",
        "322004": "https://achsnm.ernesthealth.com/wp-content/uploads/2022/01/Advanced-Care-Southern-NM-Facility-Procedure-Master-125011.xlsx",
        "673053": "https://ccrh.ernesthealth.com/wp-content/uploads/2022/01/CCRH_Chargemaster.zip",
        "533027": "https://evrh.ernesthealth.com/wp-content/uploads/2022/01/EVRH_Chargemaster.zip",
        "423030": "https://grrh.ernesthealth.com/wp-content/uploads/2022/01/GRRH_Chargemaster.zip",
        "153042": "https://lrrh.ernesthealth.com/wp-content/uploads/2022/01/LRRH_Chargemaster.zip",
        "452096": "https://lsh.ernesthealth.com/wp-content/uploads/2022/01/Lardeo-Specialty-chrg-mstr.xlsx",
        "673059": "https://lrh.ernesthealth.com/wp-content/uploads/2022/01/LRH_Chargemaster.zip",
        "673045": "https://mri.ernesthealth.com/wp-content/uploads/2022/01/MRI_Chargemaster.zip",
        "452100": "https://msh.ernesthealth.com/wp-content/uploads/2022/01/Mesquite-Specialty-chrg-mstr.xlsx",
        "033036": "https://mvrrh.ernesthealth.com/wp-content/uploads/2022/01/MVRRH_Chargemaster.zip",
        "673049": "https://nbrrh.ernesthealth.com/wp-content/uploads/2022/01/NBRRH_Chargemaster.zip",
        "062017": "https://ncltah.ernesthealth.com/wp-content/uploads/2022/01/Northern-Colorado-Advanced-Care-Facility-Procedure-Master-125031.xlsx",
        "063033": "https://ncrh.ernesthealth.com/wp-content/uploads/2022/01/NCRH_Chargemaster.zip",
        "132001": "https://niach.ernesthealth.com/wp-content/uploads/2022/01/Northern-Idaho-Advanced-Care-Procedure-Master.xlsx",
        "033041": "https://rhna.ernesthealth.com/wp-content/uploads/2022/01/RHNA_Chargemaster.zip",
        "463027": "https://nurh.ernesthealth.com/wp-content/uploads/2022/01/NURH_Chargemaster.zip",
        "363040": "https://rhno.ernesthealth.com/wp-content/uploads/2022/01/RHNO_Chargemaster.zip",
        "133027": "https://rhn.ernesthealth.com/wp-content/uploads/2022/01/RHN_Chargemaster.zip",
        "323032": "https://rhsnm.ernesthealth.com/wp-content/uploads/2022/01/Rehab-S-New-Mexico-Facility-Procedure-Master-110010.xlsx",
        "453092": "https://strh.ernesthealth.com/wp-content/uploads/2022/01/STRH_Chargemaster.zip",
        "423031": "https://sri.ernesthealth.com/wp-content/uploads/2022/01/SRI_Chargemaster.zip",
        "673063": "https://trhl.ernesthealth.com/wp-content/uploads/2022/01/TRHL_Chargemaster.zip",
        "462005": "https://uvsh.ernesthealth.com/wp-content/uploads/2022/01/Utah-Valley-Specialty-Charge-Master-120040.xlsx",
        "453091": "https://wrrh.ernesthealth.com/wp-content/uploads/2022/01/WRRH_Chargemaster.zip",
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
                xlsx_url.split("/wp-content/")[0], xlsx_url, csm_num
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
