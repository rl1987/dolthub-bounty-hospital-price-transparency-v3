#!/usr/bin/python3

import csv
from io import BytesIO
from pprint import pprint

import openpyxl
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


def main():
    cms_certification_num = "041313"

    out_f = open("041313.csv", "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    resp = requests.get(
        "https://www.ozarkhealth.net/sites/default/files/2021-01/1%2019%2021%20Pricing%20Transparency%20Data.xlsx"
    )
    print(resp.url)

    b_f = BytesIO(resp.content)

    wb = openpyxl.load_workbook(b_f)
    ws = wb.active

    in_fieldnames = None

    for in_row in ws.rows:
        values = list(map(lambda cell: cell.value, in_row))

        if in_fieldnames is None:
            in_fieldnames = values
            continue

        in_row_dict = dict(zip(in_fieldnames, values))

        pprint(in_row_dict)

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": in_row_dict.get("Service ID"),
            "internal_revenue_code": in_row_dict.get("Revenue Code"),
            "units": "",
            "description": in_row_dict.get("Service Description"),
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": in_row_dict.get("CDM Item Number"),
        }

        if out_row.get("code") is None:
            out_row["code"] = "NONE"

        if out_row.get("internal_revenue_code") is None:
            out_row["internal_revenue_code"] = "NONE"

        if out_row.get("code_disambiguator") is None:
            out_row["code_disambiguator"] = "NONE"

        if in_row_dict.get("Discounted Cash Price") is not None:
            out_row["payer"] = "CASH PRICE"
            out_row["price"] = in_row_dict.get("Discounted Cash Price")
            pprint(out_row)
            csv_writer.writerow(out_row)

        if in_row_dict.get("Gross Charge") is not None:
            out_row["payer"] = "GROSS CHARGE"
            out_row["price"] = in_row_dict.get("Gross Charge")
            pprint(out_row)
            csv_writer.writerow(out_row)

        if in_row_dict.get("Maximum Negotiated Charge") is not None:
            out_row["payer"] = "MAX"
            out_row["price"] = in_row_dict.get("Maximum Negotiated Charge")
            pprint(out_row)
            csv_writer.writerow(out_row)

        if in_row_dict.get("Minimum Negotiated Charge") is not None:
            out_row["payer"] = "MIN"
            out_row["price"] = in_row_dict.get("Minimum Negotiated Charge")
            pprint(out_row)
            csv_writer.writerow(out_row)

        for k in in_row_dict.keys():
            if (
                k.startswith("Payer Negotiated Charge: ")
                and in_row_dict.get(k) is not None
            ):
                out_row["payer"] = k.replace("Payer Negotiated Charge: ", "")
                out_row["price"] = in_row_dict[k]
                pprint(out_row)
                csv_writer.writerow(out_row)

    out_f.close()


if __name__ == "__main__":
    main()
