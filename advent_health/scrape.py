#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint
import re
import os
import json

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
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

    return filename

def process_chargemaster(cms_id, url):
    filename = download_chargemaster(url)

    in_f = open(filename, "r", encoding="cp1252")

    json_arr = json.load(in_f)
    for x in json_arr:
        if type(x) == list:
            json_arr = x
            break

    resp = requests.get(url)
    print(resp.url)

    out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for in_row in json_arr:
        pprint(in_row)
        code = in_row.get("Code")
        description = in_row.get("Description")
        if description is None:
            description = in_row.get("Charge Description")
        rev_code = in_row.get("RevCode")
        quantity = ""

        if code == "" or code is None:
            code = "NONE"

        if rev_code == "" or rev_code is None:
            rev_code = "NONE"
    
        inpatient_outpatient = "UNSPECIFIED"

        if in_row.get("type") == "Inpatient":
            inpatient_outpatient = "INPATIENT"
        elif in_row.get("type") == "Outpatient":
            inpatient_outpatient = "OUTPATIENT"

        out_row = {
            "cms_certification_num": cms_id,
            "code": code,
            "internal_revenue_code": "NONE",
            "units": quantity,
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "code_disambiguator": "NONE",
        }

        payers = list(in_row.keys())
        if "Code" in payers:
            payers.remove("Code")
        if "Description" in payers:
            payers.remove("Description")
        if "Code Type" in payers:
            payers.remove("Code Type")
        if "Type" in payers:
            payers.remove("Type")
        if "RevCode" in payers:
            payers.remove("RevCode")
        if "Payer" in payers:
            payers.remove("Payer")

        print(payers)

        for payer in payers:
            price = in_row.get(payer)
            
            if not type(price) == float and not type(price) == int:
                try:
                    price = float(price)
                except:
                    continue

            if payer == "Gross Charge":
                payer = "GROSS CHARGE"
            elif payer == "Discounted Cash Price":
                payer = "CASH PRICE"
            elif payer == "Min" or payer == "Deidentified Min":
                payer = "MIN"
            elif payer == "Max" or payer == "Deidentified Max":
                payer = "MAX"
            elif payer == "Contracted Allowed":
                payer = in_row.get("Payer")

            out_row["payer"] = payer
            out_row["price"] = price
            pprint(out_row)
            csv_writer.writerow(out_row)

    in_f.close()
    out_f.close()

def main():
    targets = {
        "102026": "https://www.adventhealth.com/sites/default/files/CDM/2022/591113901_AdventHealthConnerton_standardcharges.json",
        "110023": "https://www.adventhealth.com/sites/default/files/CDM/2022/581425000_AdventHealthGordon_standardcharges.json",
        "110050": "https://www.adventhealth.com/sites/default/files/CDM/2022/581425000_AdventHealthMurray_standardcharges.json",
        "170014": "https://www.adventhealth.com/sites/default/files/CDM/2022/830976641_AdventHealthOttawa_standardcharges.json",
        "170104": "https://www.adventhealth.com/sites/default/files/CDM/2022/480637331_AdventHealthShawneeMission_standardcharges.json",
        "100007": "https://www.adventhealth.com/sites/default/files/CDM/2022/591479658_AdventHealthOrlando_standardcharges.json",
        "100014": "https://www.adventhealth.com/sites/default/files/CDM/2022/473793197_AdventHealthNew%20Smyrna_standardcharges.json",
        "100045": "https://www.adventhealth.com/sites/default/files/CDM/2022/593256803_AdventHealthDeLand_standardcharges.json",
        "100046": "https://www.adventhealth.com/sites/default/files/CDM/2022/592108057_AdventHealthZephyrhills_standardcharges.json",
        "100055": "https://www.adventhealth.com/sites/default/files/CDM/2022/590898901_AdventHealthNorth%20Pinellas_standardcharges.json",
        "100057": "https://www.adventhealth.com/sites/default/files/CDM/2022/593140669_AdventHealthWaterman_standardcharges.json",
        "100062": "https://www.adventhealth.com/sites/default/files/CDM/2022/824372339_AdventHealthOcala_standardcharges.json",
        "100068": "https://www.adventhealth.com/sites/default/files/CDM/2022/590973502_AdventHealthDaytonaBeach_standardcharges.json",
        "100069": "https://www.adventhealth.com/sites/default/files/CDM/2022/591113901_AdventHealthCarrollwood_standardcharges.json",
        "100072": "https://www.adventhealth.com/sites/default/files/CDM/2022/593149293_AdventHealthFishMemorial_standardcharges.json",
        "100099": "https://www.adventhealth.com/sites/default/files/CDM/2022/834672945_AdventHealthLake%20Wales_standardcharges.json",
        "100109": "https://www.adventhealth.com/sites/default/files/CDM/2022/590725553_AdventHealthSebring_standardcharges.json",
        "100118": "https://www.adventhealth.com/sites/default/files/CDM/2022/592951990_AdventHealthPalmCoast_standardcharges.json",
        "100137": "https://www.adventhealth.com/sites/default/files/CDM/2022/841793121_AdventHealthHeartofFlorida_standardcharges.json",
        "100173": "https://www.adventhealth.com/sites/default/files/CDM/2022/591113901_AdventHealthTampa_standardcharges.json",
        "100211": "https://www.adventhealth.com/sites/default/files/CDM/2022/822567308_AdventHealthDade%20City_standardcharges.json",
        "100319": "https://www.adventhealth.com/sites/default/files/CDM/2022/208488713_AdventHealthWesleyChapel_standardcharges.json",
        "101300": "https://www.adventhealth.com/sites/default/files/CDM/2022/590725553_AdventHealthWauchula_standardcharges.json",
        "180043": "https://www.adventhealth.com/sites/default/files/CDM/2022/610594620_AdventHealthManchester_standardcharges.json",
        "450152": "https://www.adventhealth.com/sites/default/files/CDM/2022/742575462_AdventHealthCentral%20Texas_standardcharges.json",
        "451323": "https://www.adventhealth.com/sites/default/files/CDM/2022/742225672_AdventHealthRollinsBrook_standardcharges.json",
        "521307": "https://www.adventhealth.com/sites/default/files/CDM/2022/391365168_AdventHealthDurand_standardcharges.json"
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.adventhealth.com/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
