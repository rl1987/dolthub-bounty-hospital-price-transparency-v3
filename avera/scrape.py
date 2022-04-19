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
    ws = wb["CDM"]

    input_fieldnames = None
    payers = None

    for in_row in ws.rows:
        values = list(map(lambda cell: cell.value, in_row))
        if type(values[0]) == str and values[0].startswith("Prices"):
            continue
        pprint(values)

        if values[0] == "Facility Name":
            input_fieldnames = values
            payers = values[7:]
            payers.append("Gross Charge")
            continue

        in_row_dict = dict(zip(input_fieldnames, values))
        pprint(in_row_dict)

        code_disambiguator = "NONE"

        description = in_row_dict.get("Description")
        if description is None:
            description = in_row_dict.get("CHARGE DESCRIPTION")

        code = in_row_dict.get("CPT")

        if code == "" or code is None:
            code = "NONE"

        rev_code = in_row_dict.get("Revcode")
        if rev_code is None or rev_code == "":
            rev_code = "NONE"

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "code_disambiguator": code_disambiguator,
            "inpatient_outpatient": "UNSPECIFIED",
        }

        for payer in payers:
            price = in_row_dict.get(payer)
            if price == "" or price is None:
                continue

            price = str(price)
            if price == "N/A" or price == "Fixed":
                continue

            price = fix_price(price)

            if payer == "Gross Charge":
                payer = "GROSS CHARGES"
            elif payer == "Discounted Cash Price":
                payer = "CASH PRICE"
            elif payer == "Minimum Negotiated Rate":
                payer = "MIN"
            elif payer == "Maximum Negotiated Rate":
                payer = "MAX"

            payer = payer.replace("Negotiated Rate", "").strip()

            out_row["payer"] = payer
            out_row["price"] = price

            pprint(out_row)
            csv_writer.writerow(out_row)

    b_f.close()


def main():
    targets = {
        "161351": "https://www.avera.org/app/files/public/74012/42-0680370_Avera-Holy-Family-Hospital_Standard-Charges.xlsx",
        "161321": "https://www.avera.org/app/files/public/79147/460224743_Avera-Merrill-Pioneer-Hospital_Standard-Charges.xlsx",
        "281329": "https://www.avera.org/app/files/public/74027/47-0463911_Avera-St-Anthonys-Hospital_Standard-Charges.xlsx",
        "281331": "https://www.avera.org/app/files/public/73999/460225483_Avera-Creighton-Hospital_Standard-Charges.xlsx",
        "241343": "https://www.avera.org/app/files/public/79150/84-3156881_Granite-Falls-Health-Center_Standard-Charges.xlsx",
        "241348": "https://www.avera.org/app/files/public/74032/41-0853163_Avera-Tyler-Hospital_Standard-Charges.xlsx",
        # "241359": "https://www.avera.org/app/files/public/74016/460380552_Avera-Marshall-Regional-Medical-Center_Standard-Charges.xlsx",
        "430012": "https://www.avera.org/app/files/public/74025/46-0225483_Avera-Sacred-Heart-Hospital_Standard-Charges.xlsx",
        "430013": "https://www.avera.org/app/files/public/74023/46-0224604_Avera-Queen-of-Peace-Hospital_Standard-Charges.xlsx",
        "430014": "https://www.avera.org/app/files/public/74028/46-0226738_Avera-St-Benedict-Health-Center_Standard-Charges.xlsx",
        "430015": "https://www.avera.org/app/files/public/74030/46-0230199_Avera-St-Marys-Hospital_Standard-Charges.xlsx",
        "430016": "https://www.avera.org/app/files/public/74017/46-0024743_Avera-McKennan-Hospital_Standard-Charges.xlsx",
        "430095": "https://www.avera.org/app/files/public/74008/562143771_Avera-Heart-Hospital_Standard-Charges.xlsx",
        "431310": "https://www.avera.org/app/files/public/74003/460224743_Avera-Flandreau-Hospital_Standard-Charges.xlsx",
        "431324": "https://www.avera.org/app/files/public/74034/460224604_Avera-Weskota-Memorial-Hospital_Standard-Charges.xlsx",
        "431326": "https://www.avera.org/app/files/public/74018/460224743_Milbank-Area-Health-Care-Campus_Standard-Charges.xlsx",
        "431330": "https://www.avera.org/app/files/public/74028/46-0226738_Avera-St-Benedict-Health-Center_Standard-Charges.xlsx",
        "431331": "https://www.avera.org/app/files/public/74000/460224743_Avera-Dells-Area-Hospital_Standard-Charges.xlsx",
        "431332": "https://www.avera.org/app/files/public/74001/460224604_Avera-De-Smet-Memorial-Hospital_Standard-Charges.xlsx",
        "431337": "https://www.avera.org/app/files/public/74007/460224743_Avera-Hand-County-Memorial-Hospital_Standard-Charges.xlsx",
        "431338": "https://www.avera.org/app/files/public/74006/460224743_Avera-Gregory-Hospital_Standard-Charges.xlsx",
        "161368": "https://www.avera.org/app/files/public/74004/420928451_Floyd-Valley-Healthcare_Standard-Charges.xlsx",
        # "161336": "https://www.avera.org/app/files/public/74009/420932564_Hegg-Health-Center_Standard-Charges.xlsx",
        "160124": "https://www.avera.org/app/files/public/74013/426037582_Lakes-Regional-Healthcare_Standard-Charges.xlsx",
        "161346": "https://www.avera.org/app/files/public/74026/420796764_Sioux-Center-Health_Standard-Charges.xlsx",
        "241374": "https://www.avera.org/app/files/public/74020/411392082_Pipestone-County-Medical-Center_Standard-Charges.xlsx",
        "431308": "https://www.avera.org/app/files/public/74002/460246437_Eureka-Community-Health-Services_Standard-Charges.xlsx",
        "431313": "https://www.avera.org/app/files/public/79149/460232450_Freeman-Regional-Hospital_Standard-Charges.xlsx",
        "431318": "https://www.avera.org/app/files/public/79148/460369929_Bowdle-Healthcare-Center_Standard-Charges.xlsx",
        "431317": "https://www.avera.org/app/files/public/74014/466015787_Landmann-Jungman-Memorial-Hospital_Standard-Charges.xlsx",
        "431306": "https://www.avera.org/app/files/public/74022/460239781_Platte-Health-Center_Standard-Charges.xlsx",
        "431327": "https://www.avera.org/app/files/public/74031/460225414_St-Michaels-Hospital_Standard-Charges.xlsx",
        "431315": "https://www.avera.org/app/files/public/74033/460226283_Wagner-Community-Memorial-Hospital_Standard-Charges.xlsx",
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
            'UPDATE `hospitals` SET `homepage_url` = "https://www.avera.org", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                xlsx_url, csm_num
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
