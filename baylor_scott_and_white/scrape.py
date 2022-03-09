#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO
from pprint import pprint
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

def process_chargemaster(cms_id, url):
    resp = requests.get(url)
    print(resp.url)

    data_starts_at = resp.text.find("Patient Type")

    s_f = StringIO(resp.text[data_starts_at:])

    out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    csv_reader = csv.DictReader(s_f)

    for in_row in csv_reader:
        pprint(in_row)

        inpatient_outpatient = in_row.get("Patient Type")
        if inpatient_outpatient == "Inpatient":
            inpatient_outpatient = "INPATIENT"
        elif inpatient_outpatient == "Outpatient":
            inpatient_outpatient = "OUTPATIENT"
        else:
            inpatient_outpatient = "UNSPECIFIED"

        payers = list(in_row.keys())[10:]

        code = in_row.get("CPT / HCPCS Code")
        if code == "N/A" or code == "":
            code = "NONE"

        rev_code = in_row.get("Default Rev Code")
        if rev_code == "N/A" or rev_code == "":
            rev_code = "NONE"

        description = in_row.get("Procedure Name")
        code_disambiguator = str(uuid.uuid4())

        out_row = {
            "cms_certification_num": cms_id,
            "code": code,
            "internal_revenue_code": rev_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": inpatient_outpatient,
            "code_disambiguator": code_disambiguator,
        }

        for payer in payers:
            price = in_row.get(payer).strip()
            if price == "**" or price == "" or price == "N/A" or price == "-":
                continue

            price = fix_price(price)
            
            payer = payer.strip()

            if payer == "Gross Charge":
                payer = "GROSS CHARGE"
            elif payer == "Discounted Cash Price":
                payer = "CASH PRICE"
            elif payer == "De-Identified Minimum Reimbursement*":
                payer = "MIN"
            elif payer == "De-Identified Maximum Reimbursement*":
                payer = "MAX"

            out_row['price'] = price
            out_row['payer'] = payer

            pprint(out_row)

            csv_writer.writerow(out_row)

    out_f.close()

def main():
    targets = {
        "450054": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/74-1166904_BAYLOR%20SCOTT%20%26%20WHITE%20%20MEMORIAL%20HOSPITAL%20AT%20TEMPLE_standardcharges.csv",
        "450101": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/74-1161944_HILLCREST%20BAPTIST%20MEDICAL%20CENTER_standardcharges.csv",
        "450137": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/75-1008430_BAYLOR%20ALL%20SAINTS%20MEDICAL%20CENTER%20AT%20FORT%20WORTH_standardcharges.csv",
        "450372": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/75-1844139_BAYLOR%20SCOTT%20&%20WHITE%20MEDICAL%20CENTER%20AT%20WAXAHACHIE_standardcharges.csv",
        "450563": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/75-1777119_BAYLOR%20SCOTT%20&%20WHITE%20REGIONAL%20MEDICAL%20CENTER%20AT%20GRAPEVINE_standardcharges.csv",
        "450742": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/26-0194016_BAYLOR%20SCOTT%20&%20WHITE%20MEDICAL%20CENTER%20LAKE%20POINTE_standardcharges.csv",
        "450885": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/82-4052186_BAYLOR%20MEDICAL%20CENTER%20CENTENNIAL_standardcharges.csv",
        "670082": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/75-1037591_BAYLOR%20SCOTT%20&%20WHITE%20%20MEDICAL%20CENTER%20AT%20MCKINNEY_standardcharges.csv",
        "670108": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/46-4007700_BAYLOR%20SCOTT%20&%20WHITE%20%20MEDICAL%20CENTER%20AT%20MARBLE%20FALLS_standardcharges.csv",
        "670131": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/81-3040663_BAYLOR%20SCOTT%20&%20WHITE%20%20MEDICAL%20CENTER%20BUDA_standardcharges.csv",
        "451374": "https://www.bswhealth.com/SiteCollectionDocuments/patient-tools/estimate-cost-of-care/74-1595711_BAYLOR%20SCOTT%20&%20WHITE%20%20MEDICAL%20CENTER%20AT%20TAYLOR_standardcharges.csv"
    }
    
    out_f = open("hospitals.sql", "w", encoding="utf-8")

    for cms_id in targets.keys():
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        out_f.write('UPDATE `hospitals` SET `homepage_url` = "https://www.bswhealth.com", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(url, cms_id))

    out_f.close()

if __name__ == "__main__":
    main()

