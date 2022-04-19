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


def scrape_sheet(cms_certification_num, ws, inpatient_outpatient):
    keys = None

    payer = None

    for row in ws:
        values = list(map(lambda cell: cell.value, row))

        if len(values) >= 2 and values[0] == "Payer":
            payer = values[1]

        if "Description" in values or "FSC Description" in values:
            keys = values
            continue

        if keys is None:
            continue

        in_row_dict = dict(zip(keys, values))
        pprint(in_row_dict)

        code = in_row_dict.get("HCPCS")
        if code is None or code == "":
            code = in_row_dict.get("MS-DRG")
        if code is None or code == "":
            code = in_row_dict.get("APC")
        if code is None or code == "":
            code = "NONE"

        if in_row_dict.get("Modifier") is not None:
            code += "-" + in_row_dict.get("Modifier")

        rev_code = in_row_dict.get("Revenue Code")
        if rev_code is None or rev_code == "":
            rev_code = "NONE"

        description = in_row_dict.get("Description")
        if description is None:
            description = in_row_dict.get("FSC Description")

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "code_disambiguator": "NONE",
        }

        if in_row_dict.get("Unit Price") is not None:
            payer = "GROSS CHARGE"
            price = in_row_dict.get("Unit Price")
            out_row["payer"] = payer
            out_row["price"] = price
            yield out_row

        if in_row_dict.get("Discount Cash Price") is not None:
            payer = "CASH PRICE"
            price = in_row_dict.get("Discount Cash Price")
        elif in_row_dict.get("De-Identified Minimum Negotiated Charge") is not None:
            payer = "MIN"
            price = in_row_dict.get("De-Identified Minimum Negotiated Charge")
        elif in_row_dict.get("De-Identified Maximum Negotiated Charge") is not None:
            payer = "MAX"
            price = in_row_dict.get("De-Identified Maximum Negotiated Charge")
        elif in_row_dict.get("Payer Specific Negotiated Charge"):
            price = in_row_dict.get("Payer Specific Negotiated Charge")
        else:
            continue

        out_row["payer"] = payer
        out_row["price"] = price
        yield out_row


def scrape_hospital_data(cms_certification_num, url):
    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    resp = requests.get(url)
    print(resp.url)

    b_f = BytesIO(resp.content)

    wb = openpyxl.load_workbook(b_f)

    for sheet_name in wb.sheetnames:
        if sheet_name == "Tab Summary":
            continue

        inpatient_outpatient = "UNSPECIFIED"
        if sheet_name.startswith("IP") or sheet_name.startswith("Inpatient"):
            inpatient_outpatient = "INPATIENT"
        elif sheet_name.startswith("OP"):
            inpatient_outpatient = "OUTPATIENT"

        ws = wb[sheet_name]

        for row in scrape_sheet(cms_certification_num, ws, inpatient_outpatient):
            pprint(row)
            csv_writer.writerow(row)

    out_f.close()


def main():
    targets = {
        "340109": "https://www.sentara.com/Assets/CSV/463846081_sentara-albemarle-medical-center_standardcharges.xlsx",
        "490004": "https://www.sentara.com/Assets/CSV/540506331_sentara-rmh-medical-center_standardcharges.xlsx",
        "490007": "https://www.sentara.com/Assets/CSV/541547408_sentara-norfolk-general-hospital_standardcharges.xlsx",
        "490013": "https://www.sentara.com/Assets/CSV/540648699_sentara-halifax-regional-hospital_standardcharges.xlsx",
        "490044": "https://www.sentara.com/Assets/CSV/541547408_sentara-obici-hospital_standardcharges.xlsx",
        "490046": "https://www.sentara.com/Assets/CSV/541547408_sentara-leigh-hospital_standardcharges.xlsx",
        "490057": "https://www.sentara.com/Assets/CSV/541547408_sentara-virginia-beach-general-hospital_standardcharges.xlsx",
        "490066": "https://www.sentara.com/Assets/CSV/541547408_sentara-williamsburg-regional-medical-center_standardcharges.xlsx",
        "490077": "https://www.sentara.com/Assets/CSV/540261840_sentara-martha-jefferson-hospital_standardcharges.xlsx",
        "490093": "https://www.sentara.com/Assets/CSV/541547408_sentara-careplex-hospital_standardcharges.xlsx",
        "490113": "https://www.sentara.com/Assets/CSV/540853898_sentara-northern-virginia-medical-center_standardcharges.xlsx",
        "490119": "https://www.sentara.com/Assets/CSV/273208969_sentara-princess-anne-hospital_standardcharges.xlsx",
    }

    h_f = open("hospitals.sql", "w")

    for csm_num in targets.keys():
        url = targets[csm_num]

        scrape_hospital_data(csm_num, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.sentara.com", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, csm_num
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
