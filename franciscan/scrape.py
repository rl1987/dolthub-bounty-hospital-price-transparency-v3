#!/usr/bin/python3

import csv
from pprint import pprint
from io import StringIO

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

def process_chargemaster(cms_certification_num, url):
    resp = requests.get(url)
    print(resp.url)

    starts_at = resp.text.find("Description")
    s_f = StringIO(resp.text[starts_at:])

    csv_reader = csv.DictReader(s_f)

    out_f = open("{}.csv".format(cms_certification_num), "w", encoding="utf-8")

    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES)
    csv_writer.writeheader()

    for in_row in csv_reader:
        payers = list(in_row.keys())[4:]

        code = in_row.get("CPT_HCPCS")
        if code == "":
            code = "NONE"
        else:
            code = code.split(" ")[-1]

        internal_revenue_code = in_row.get("Billing_Code")
        description = in_row.get("Description")
        description = description.split("Copyright")[0].strip()
        description = description.replace("\n", " ")

        if len(description) > 2048:
            description = description[:2048]

        out_row = {
            "cms_certification_num": cms_certification_num,
            "code": code,
            "internal_revenue_code": internal_revenue_code,
            "units": "",
            "description": description,
            "inpatient_outpatient": "UNSPECIFIED",
            "code_disambiguator": description,
        }

        for payer in payers:
            price = in_row.get(payer)
            if not price.startswith("$"):
                continue

            if payer == "Gross_Charge":
                payer = "GROSS CHARGE"
            elif payer == "Discounted_Cash_Price":
                payer = "CASH PRICE"
            elif payer == "De-Identified_Minimum_Negotiated_Rate":
                payer = "MIN"
            elif payer == "De-Identified_Maximum_Negotiated_Rate":
                payer = "MAX"
            else:
                payer = payer.replace("_Payer_Specific_Negotiated_Rate", "")

            out_row["payer"] = payer
            out_row["price"] = fix_price(price)

            pprint(out_row)
            csv_writer.writerow(out_row)

    out_f.close()


def main():
    targets = {
        "150022": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/352085495_franciscan-health-crawfordsville_standardcharges.csv?rev=0035be8710bc418eb11e3fdec3b7749c",
        "150126": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/352074283_franciscan-health-crown-point_standardcharges.csv?rev=142ebe678e9c4a29b00a463c0158909b",
        "150090": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/351835133_franciscan-health-dyer_standardcharges.csv?rev=2e5b87bc6d954dbfa38d914e697ebbd6",
        "150004": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/351835133_franciscan-health-hammond_standardcharges.csv?rev=19dd366460cf4559a12aa0aa9ff9f1eb",
        "150162": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/350913537_franciscan-health-indianapolis_standardcharges.csv?rev=9cf010164dcb4235aad30bf821cf4707",
        "150109": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/352056396_franciscan-health-lafayette_standardcharges.csv?rev=85273904b3b84ae0a108202e3577a18e",
        "150015": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/350876394_franciscan-health-michigan-city_standardcharges.csv?rev=c6471bb45e3348989a5fd51df4f51e44",
        "150057": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/350913537_franciscan-health-mooresville_standardcharges.csv?rev=20ca760e514f4b35b55c7f4d5302f2d0",
        "150165": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/352472136_franciscan-health-munster_standardcharges.csv?rev=17afc79b1b2c431380ef6e5aec6c9096",
        "140172": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/362167869_franciscan-health-olympia-fields_standardcharges.csv?rev=1b516e0d3a7241538ae5d4ce6639d322",
        "151324": "https://media.franciscanhealth.org/-/patient-resources/standard-charges/473825106_franciscan-health-rensselaer_standardcharges.csv?rev=e2b490e6539c4342a2f96e30f201cbd5"
    }

    h_f = open("hospitals.sql", "w")

    for cms_id in targets:
        url = targets[cms_id]
        process_chargemaster(cms_id, url)

        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.franciscanhealth.org/", `chargemaster_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                url, cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
