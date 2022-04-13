#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
import uuid

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


def fix_price(price_str):
    price_str = price_str.replace("$", "").replace(",", "").strip()

    if "." in price_str and len(price_str.split(".")[-1]) > 2:
        price_str = price_str.split(".")[0] + "." + price_str.split(".")[-1][:2]

    return price_str


def scrape_hospital_data(cms_certification_num, xlsx_url, csv_writer):
    resp = requests.get(xlsx_url)
    print(resp)
    print(resp.url)
    
    s_f = StringIO(resp.text)

    csv_reader = csv.DictReader(s_f)

    input_fieldnames = None
    payers = None

    for in_row_dict in csv_reader:
        pprint(in_row_dict)
        if payers is None:
            payers = list(in_row_dict.keys())[9:]

        code_disambiguator = in_row_dict.get("CHARGE CODE/PACKAGE")
        if code_disambiguator is None:
            code_disambiguator = in_row_dict.get("CHARGE CODE/ PACKAGE")
        if code_disambiguator is None:
            code_disambiguator = in_row_dict.get("CHARGE CODE PACKAGE")
        if code_disambiguator == "" or code_disambiguator is None:
            code_disambiguator = "NONE"

        description = in_row_dict.get("ChargeDesc")
        if description is None:
            description = in_row_dict.get("CHARGE DESCRIPTION")

        code = in_row_dict.get("CPT")
        if code is None:
            code = in_row_dict.get("CPT\xef\xbf\xbd/HCPCS")

        modifiers = in_row_dict.get("MODIFIERS")

        if code == "" or code is None:
            code = "NONE"
        else:
            if modifiers != "" and modifiers is not None:
                code += str(modifiers)

        rev_code = in_row_dict.get("RevCode")
        if rev_code is None:
            rev_code = in_row_dict.get("REV CODE")

        if rev_code is None or rev_code == "":
            rev_code = "NONE"

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "code_disambiguator": code_disambiguator,
        }

        for payer in payers:
            price = in_row_dict.get(payer)
            if price == "" or price is None or "%" in price or price == "Need Rates" or price == "Case Rate" or price == "Exclusion":
                continue

            price = str(price)
            price = fix_price(price)

            payer = payer.strip()

            inpatient_outpatient = "UNSPECIFIED"

            if payer == "GROSS CHARGES":
                payer = "GROSS CHARGE"
            elif payer == "Self Pay Price" or payer == "SELF PAY CASH PRICE":
                payer = "CASH PRICE"
            elif payer == "MIN NEGOTIATED RATE":
                payer = "MIN"
            elif payer == "MAX NEGOTIATED RATE":
                payer = "MAX"
            else:
                if "IP Rate" in payer:
                    inpatient_outpatient = "INPATIENT"
                    payer = payer.replace("IP Rate", "").strip()
                elif "OP Rate" in payer:
                    inpatient_outpatient = "OUTPATIENT"
                    payer = payer.replace("OP Rate", "").strip()

                payer = payer.replace("Type", "").replace("INPATIENT", "").strip()

            out_row["inpatient_outpatient"] = inpatient_outpatient
            out_row["payer"] = payer
            out_row["price"] = price

            pprint(out_row)
            csv_writer.writerow(out_row)


def main():
    targets = {
        "230141": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-2383119_McLarenFlint_standardcharges.csv",
        "230167": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-1434090_McLarenGreaterLansing_standardcharges.csv",
        "230193": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-2689033_McLarenLapeer_standardcharges.csv",
        "230207": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-1428164_McLarenOakland_standardcharges.csv",
        "230216": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-1369611_McLarenPortHuron_standardcharges.csv",
        "230227": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-1218516_McLarenMacomb_standardcharges.csv",
        "231329": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-3426063_McLarenCaroCommunityHospital_standardcharges.csv", 
        "232020": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-3161753_McLarenBaySpecialCare_standardcharges.csv",
        "230041": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-1976271_McLarenBayRegion_standardcharges.csv",
        "230080": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-1420304_McLarenCentral_standardcharges.csv",
        "230105": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-2146751_McLarenNorthernMichigan_standardcharges.csv",
        "230118": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-1474929_McLarenThumbRegion_standardcharges.csv", # !!!
        "230297": "https://www.mclaren.org/Uploads/Public/Documents/corporate/ChargeMasterFile/2022/38-1613280_KarmanosCancerInstitute_standardcharges.csv"
    }

    h_f = open("hospitals.sql", "w")

    for csm_num in targets.keys():
        out_f = open("{}.csv".format(csm_num), "w", encoding="utf-8")

        csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
        csv_writer.writeheader()

        url = targets[csm_num]

        scrape_hospital_data(csm_num, url, csv_writer)

        out_f.close()

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.mclaren.org", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, csm_num
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
