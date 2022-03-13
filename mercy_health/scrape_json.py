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
    json_arr = json.load(in_f)
    in_f.close()

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    for entry in json_arr:
        code = entry.get("Code")
        if code is None or code == "":
            code = "NONE"
        else:
            code = code.split(" ")[-1]

        rev_code = entry.get("Rev Code")
        if rev_code is None or rev_code == "":
            rev_code = "NONE"
        else:
            rev_code = rev_code.split(" ")[0]

        description = entry.get("Procedure Description")

        row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": description,
        }

        for k in entry.keys():
            if k == "IP Price":
                row['payer'] = "GROSS CHARGE"
                row['price'] = "{:.2f}".format(entry[k])
                row['inpatient_outpatient'] = "INPATIENT"
                csv_writer.writerow(row)
                pprint(row)
                row['inpatient_outpatient'] = "UNSPECIFIED"
            elif k == "OP Price":
                row['payer'] = "GROSS CHARGE"
                row['price'] = "{:.2f}".format(entry[k])
                row['inpatient_outpatient'] = "OUTPATIENT"
                csv_writer.writerow(row)
                pprint(row)
                row['inpatient_outpatient'] = "UNSPECIFIED"
            elif k == "<Self-pay>":
                row['payer'] = "CASH PRICE"
                row['price'] = "{:.2f}".format(entry[k])
                csv_writer.writerow(row)
                pprint(row)
            elif k == "Min":
                row['payer'] = "MIN"
                row['price'] = "{:.2f}".format(entry[k])
                csv_writer.writerow(row)
                pprint(row)
            elif k == "Max":
                row['payer'] = "MAX"
                row['price'] = "{:.2f}".format(entry[k])
                csv_writer.writerow(row)
                pprint(row)
            elif "[" in k:
                row['payer'] = k
                row['price'] = "{:.2f}".format(entry[k])
                csv_writer.writerow(row)
                pprint(row)
        
    out_f.close()

def main():
    targets = {
        "360016": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/271408630_jewish_standardcharges.ashx?la=en",
        "360001": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/310537085_anderson_standardcharges.ashx?la=en",
        "360236": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/310830955_clermont_standardcharges.ashx?la=en",
        "360056": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/310538532_fairfield_standardcharges.ashx?la=en",
        "360234": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/311091597_west_standardcharges.ashx?la=en", 
        "360066": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/341105619_stritas_standardcharges.ashx?la=en",
        "361306": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/340864230_mercy-health-allen_standardcharges.ashx?la=en",
        "360172": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/340714704_lorain_standardcharges.ashx?la=en",
        "361312": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/310785684_mercy-health-urbana_standard-charges.ashx?la=en",
        "360086": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/310785684_springfield-regional_standardcharges.ashx?la=en",
        "360112": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/344428250_st-vincent_standardcharges.ashx?la=en",
        "360081": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/344445373_st-charles_standardcharges.ashx?la=en",
        "360270": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/020701635_defiance_standardcharges.ashx?la=en",
        "360089": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/344431174_tiffin_standardcharges.ashx?la=en",
        "361310": "https://www.mercy.com/-/media/mercy/patient-resources/hospital-pricing-transparency/341577110_willard_standardcharges.ashx?la=en",
    }
    out_f = open("hospitals_json.sql", "w", encoding="utf-8")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        out_f.write('UPDATE `hospitals` SET `homepage_url` = "https://www.mercy.com", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(url, cms_id))

    out_f.close()

if __name__ == "__main__":
    main()

