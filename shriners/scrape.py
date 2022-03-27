#!/usr/bin/python3

import csv
from pprint import pprint
from io import BytesIO
import uuid

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


def fix_price(price_str):
    price_str = price_str.replace("$", "").replace(",", "").strip()

    if "." in price_str and len(price_str.split(".")[-1]) > 2:
        price_str = price_str.split(".")[0] + "." + price_str.split(".")[-1][:2]

    return price_str


def scrape_hospital_data(cms_certification_num, xlsx_url, csv_writer):
    resp = requests.get(xlsx_url)
    print(resp)
    print(resp.url)

    b_f = BytesIO(resp.content)

    wb = openpyxl.load_workbook(b_f)
    ws = wb.active

    input_fieldnames = None
    payers = None

    for in_row in ws.rows:
        values = list(map(lambda cell: cell.value, in_row))
        if type(values[0]) == str and values[0].upper().startswith("LAST"):
            continue

        if values[0] == "FileRowID" or values[0] == "CDM NUMBER":
            input_fieldnames = values
            payers = values[9:]
            continue

        in_row_dict = dict(zip(input_fieldnames, values))
        pprint(in_row_dict)

        code_disambiguator = "NONE"

        description = in_row_dict.get("ChargeDesc")
        if description is None:
            description = in_row_dict.get("CHARGE DESCRIPTION")

        code = in_row_dict.get("CPT")
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
            if price == "" or price is None:
                continue

            price = str(price)
            price = fix_price(price)

            payer = payer.strip()

            inpatient_outpatient = "UNSPECIFIED"

            if payer == "GrossCharges":
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

            out_row["inpatient_outpatient"] = inpatient_outpatient
            out_row["payer"] = payer
            out_row["price"] = price

            pprint(out_row)
            csv_writer.writerow(out_row)

    b_f.close()


def main():
    targets = {
        "223304": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_bos_draft_mr_cdm_210713_v2_final.ashx",
        "143302": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_chicago_draft_mr_cdm_210712_v2_final.ashx",
        "423300": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_greenville_draft_mr_cdm_210622_v1_final.ashx",
        "123301": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_honolulu_draft_mr_cdm_210623_v1_final.ashx",
        "223303": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_springfield_draft_mr_cdm_210625_v1_final.ashx",
        "053311": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_norcal_draft_mr_cdm_210623_v1_final.ashx",
        "393309": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_philadelphia_draft_mr_cdm_210608_v1_final.ashx",
        "383300": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_portland_draft_mr_cdm_210712_v2_final.ashx",
        "193301": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_shreveport_draft_mr_cdm_210909_v3_final.ashx",
        "503302": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_spokane_draft_mr_cdm_210712_v2_final.ashx",
        "263304": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_stlouis_draft_mr_cdm_210713_v2_final.ashx",
        "453311": "https://www.shrinerschildrens.org/-/media/files/shc/other/standard-charges/2021/shriners_galveston_draft_mr_cdm_210909_v2_final.ashx",
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
            'UPDATE `hospitals` SET `homepage_url` = "https://www.shrinerschildrens.org/en", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                xlsx_url, csm_num
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
