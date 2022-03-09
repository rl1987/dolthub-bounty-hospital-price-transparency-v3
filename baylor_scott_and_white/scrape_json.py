#!/usr/bin/python3

import csv
from pprint import pprint
from io import BytesIO
import json
from urllib.request import urlretrieve

import subprocess

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
    print(url)

    subprocess.run("curl -s {} -o charges.json".format(url), shell=True)

    in_f = open("charges.json", "r")
    json_dict = json.load(in_f)
    in_f.close()

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    disamb = dict()

    for data_dict in json_dict.get('data'):
        if len(data_dict) == 0:
            continue

        data_dict = data_dict[0]
        description = data_dict.get("code description")
        if description is None:
            continue

        code = data_dict.get("code")
        code_type = data_dict.get("code type")
        payer = data_dict.get("payer")
        gross = data_dict.get("gross charge")
        discounted = data_dict.get("discounted cash price")
        min_price = data_dict.get("de-identified minimum negotiated charge")
        max_price = data_dict.get("de-identified maximum negotiated charge")
        code_disambiguator = disamb.get(code)
        if code_disambiguator is None:
            code_disambiguator = 1
        else:
            code_disambiguator += 1

        disamb[code] = code_disambiguator

        row = {
            "cms_certification_num": cms_certification_num,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": str(code_disambiguator),
        }

        if code_type == "revCode":
            row["code"] = "NONE"
            row["internal_revenue_code"] = code
        else:
            row["code"] = code
            row["internal_revenue_code"] = "NONE"

        if gross is not None:
            row["payer"] = "GROSS CHARGE"
            row["price"] = gross
            pprint(row)
            csv_writer.writerow(row)

        if discounted is not None:
            row["payer"] = "CASH PRICE"
            row["price"] = discounted
            pprint(row)
            csv_writer.writerow(row)

        if min_price is not None:
            row["payer"] = "MIN"
            row["price"] = min_price
            pprint(row)
            csv_writer.writerow(row)

        if max_price is not None:
            row["payer"] = "MAX"
            row["price"] = max_price
            pprint(row)
            csv_writer.writerow(row)
        
    out_f.close()

def main():
    targets = {
        "670060": "https://bswhealthsunnyvale.com/wp-content/uploads/2021/10/510570864BaylorScottWhiteMedicalCenterSunnyvalestandardcharges22522.json",
        "450422": "https://bayloruptown.com/wp-content/uploads/2022/02/752829613BaylorMedicalCenteratUptownstandardcharges.json",
        "450880": "https://bshfw.com/wp-content/uploads/2022/02/752658178BaylorSurgicalHospitalatFortWorthstandardcharges.json",
        "670076": "https://baylorsherman.com/wp-content/uploads/2022/02/611762781BaylorScottWhiteSurgicalHospitalatShermanstandardcharges222.json",
        "450864": "https://bswarlington.com/wp-content/themes/medicalplus-v1-052/261578178_BaylorOrthopedicandSpineHospitalatArlington_standardcharges-updates.json",
    }
    out_f = open("hospitals_json.sql", "w", encoding="utf-8")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        out_f.write('UPDATE `hospitals` SET `homepage_url` = "{}", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(url.split("/wp-content")[0], url, cms_id))

    out_f.close()

if __name__ == "__main__":
    main()

