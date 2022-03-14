#!/usr/bin/python3

import csv
from pprint import pprint

import requests
from lxml import etree


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
    resp = requests.get(url)
    print(resp.url)

    tree = etree.fromstring(resp.text)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    for in_row in tree.xpath("//row"):
        code = in_row.xpath("./CPT/text()")
        if len(code) == 0:
            code = "NONE"
        else:
            code = code[0]

        rev_code = in_row.xpath("./Rev/text()")
        if len(rev_code) == 0:
            rev_code = "NONE"
        else:
            rev_code = rev_code[0]

        code_disambiguator = in_row.xpath("./Chargecode_DRG_CPT/text()")
        if len(code_disambiguator) == 0:
            code_disambiguator = "NONE"
        else:
            code_disambiguator = code_disambiguator[0]

        description = in_row.xpath("./Description/text()")
        if len(description) == 0:
            description = "NONE"
        else:
            description = description[0]

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": code_disambiguator,
        }

        for child in in_row.iterchildren():
            key = child.tag
            value = child.text

            if value == "" or value is None:
                continue

            value = value.replace(",", "")

            payer = None

            if key == "_1_1_22_Fee":
                payer = "GROSS CHARGE"
            elif key == "SELF_PAY":
                payer = "CASH PRICE"
            elif key == "MIN" or key == "MAX":
                payer = key
            elif key.startswith("_2022_"):
                payer = key.replace("_2022_", "")

            if payer is None:
                continue

            out_row["payer"] = payer
            out_row["price"] = value
            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()


def main():
    targets = {
        "140208": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/362169147_advocate-christ-medical-center_standardcharges.xml",
        "140202": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/262525968_advocate-condell-medical-center_standardcharges.xml",
        "140288": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/362169147_advocate-good-samaritan-hospital_standardcharges.xml",
        "140291": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/362169147_advocate-good-shepherd-hospital_standardcharges.xml",
        "140182": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/363196629_advocate-illinois-masonic-medical-center_standardcharges.xml",
        "140223": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/362169147_advocate-lutheran-general-hospital_standardcharges.xml",
        "140030": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/362167920_advocate-sherman-hospital_standardcharges.xml",
        "140250": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/362169147_advocate-south-suburban-hospital_standardcharges.xml",
        "140048": "https://www.advocatehealth.com/assets/documents/hospital-pricing-information/362169147_advocate-trinity-hospital_standardcharges.xml",
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.advocatehealth.com/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
