#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint

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


def process_chargemaster(cms_certification_num, url):
    resp = requests.get(url)
    print(resp.url)

    csv_reader = csv.reader(StringIO(resp.text))

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    next(csv_reader)
    next(csv_reader)
    next(csv_reader)

    input_fieldnames = next(csv_reader)

    payers = input_fieldnames[8:]

    for in_row in csv_reader:
        in_row_dict = dict(zip(input_fieldnames, in_row))

        if len(in_row_dict) == 0:
            break

        pprint(in_row_dict)

        code = in_row_dict.get("CPT HCPCS Code")
        if code == "":
            code = "NONE"

        internal_revenue_code = in_row_dict.get("Revenue Code")
        if internal_revenue_code == "":
            internal_revenue_code = "NONE"

        code_disambiguator = in_row_dict.get("Procedure Code")

        units = in_row_dict.get("Rx Unit Multiplier")
        if units == "NA":
            units = ""

        description = in_row_dict.get("Procedure Description")

        price_tier = in_row_dict.get("Price Tier")
        inpatient_outpatient = "UNSPECIFIED"
        if price_tier == "Inpatient":
            inpatient_outpatient = "INPATIENT"
        elif price_tier == "Outpatient":
            inpatient_outpatient = "OUTPATIENT"

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": internal_revenue_code,
            "units": units,
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "code_disambiguator": code_disambiguator,
        }

        for payer in payers:
            price = in_row_dict.get(payer)

            if price == "" or price == "N/A" or price is None:
                continue

            if "." in price and len(price.split(":")[-1]) == 4:
                price = price[:-2]

            if payer == "Gross Charge":
                payer = "GROSS CHARGE"
            elif payer == "Discounted Cash Price":
                payer = "CASH PRICE"
            elif payer == "De-identified minimum negotiated charge":
                payer = "MIN"
            elif payer == "De-identified maximum negotiated charge":
                payer = "MAX"

            out_row["payer"] = payer
            out_row["price"] = price

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()


def main():
    targets = {
        "050455": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHBBAKERSFIELDCA&type=CDMWithoutLabel",
        "051317": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHCLCLEARLAKECA&type=CDMWithoutLabel",
        "050608": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbDRMCDELANOCA&type=CDMWithoutLabel",
        "050239": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbGAMCGLENDALECA&type=CDMWithoutLabel",
        "050121": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbHCMCHANFORDCA&type=CDMWithoutLabel",
        "051310": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHHMWILLITSCA&type=CDMWithoutLabel",
        "050336": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHLMLODICA&type=CDMWithoutLabel",
        "050192": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHRREEDLEYCA&type=CDMWithoutLabel",
        "050133": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbRMHMARYSVILLECA&type=CDMWithoutLabel",
        "050236": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHSVSIMIVALLEYCA&type=CDMWithoutLabel",
        "050335": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHSSONORACA&type=CDMWithoutLabel",
        "050013": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHSHSAINTHELENACA&type=CDMWithoutLabel",
        "051301": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbTHTEHACHAPICA&type=CDMWithoutLabel",
        "050784": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHTTULARECA&type=CDMWithoutLabel",
        "050301": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbUkiahValleyCA&type=CDMWithoutLabel",
        "054074": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHSHSAINTHELENACA&type=CDMWithoutLabel",  # XXX: mistaken link on the site?
        "120006": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHCKAILUAHI&type=CDMWithoutLabel",
        "380060": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAMCPORTLANDOR&type=CDMWithoutLabel",
        "381317": "https://apps.para-hcfs.com/PTT/FinalLinks/Reports.aspx?dbName=dbAHTTILLAMOOKOR&type=CDMWithoutLabel",
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.adventisthealth.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
