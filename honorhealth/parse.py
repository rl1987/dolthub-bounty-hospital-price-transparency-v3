#!/usr/bin/python3

import csv
import json
import subprocess
from pprint import pprint

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

CMS_IDS = ["030014", "030038", "030087", "030092", "030123"]


def main():
    subprocess.run(
        "wget https://www.honorhealth.com/sites/default/files/patients-visitors/pricing-transparency.zip",
        shell=True,
    )
    subprocess.run("unzip pricing-transparency.zip", shell=True)

    in_f = open("pricing-transparency.json", "r")
    json_arr = json.load(in_f)
    in_f.close()

    h_f = open("hospitals.sql", "w")

    for cms_id in CMS_IDS:
        out_f = open("{}.csv".format(cms_id), "w", encoding="utf-8")

        csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
        csv_writer.writeheader()

        for entry in json_arr:
            code_type = entry.get("code_type").strip()

            if code_type == "Rev Code":
                rev_code = entry.get("code")
                code = "NONE"
            else:
                code = entry.get("code")
                rev_code = "NONE"

            description = entry.get("desc")

            units = entry.get("ndc_quant")
            if units is None:
                units = ""

            out_row = {
                "cms_certification_num": cms_id,
                "code": code,
                "internal_revenue_code": rev_code,
                "units": units,
                "description": description,
                "inpatient_outpatient": "UNSPECIFIED",
                "code_disambiguator": "NONE",
            }

            gross = entry.get("gross_charge")
            if (
                gross is not None
                and not "-" in gross
                and gross.strip() != ""
                and not "-" in gross
            ):
                out_row["payer"] = "GROSS CHARGE"
                out_row["price"] = gross.replace("$", "").replace(",", "").strip()
                pprint(out_row)
                csv_writer.writerow(out_row)

            discounted = entry.get("discounted_cash_price")
            if (
                discounted is not None
                and not "-" in discounted
                and discounted.strip() != ""
                and not "-" in discounted
            ):
                out_row["payer"] = "CASH PRICE"
                out_row["price"] = discounted.replace("$", "").replace(",", "").strip()
                pprint(out_row)
                csv_writer.writerow(out_row)

            min_price = entry.get("deidentified_min_neg_rate")
            if (
                min_price is not None
                and not "-" in min_price
                and min_price.strip() != ""
                and not "-" in min_price
            ):
                out_row["payer"] = "MIN"
                out_row["price"] = min_price.replace("$", "").replace(",", "").strip()
                pprint(out_row)
                csv_writer.writerow(out_row)

            max_price = entry.get("deidentified_max_neg_rate")
            if (
                max_price is not None
                and not "-" in max_price
                and max_price.strip() != ""
                and not "-" in max_price
            ):
                out_row["payer"] = "MAX"
                out_row["price"] = max_price.replace("$", "").replace(",", "").strip()
                pprint(out_row)
                csv_writer.writerow(out_row)

            plan = entry.get("plan")
            plan_price = entry.get("plan_negotiated_rate")
            if (
                plan_price is not None
                and not "-" in plan_price
                and plan_price.strip() != ""
            ):
                plan_price.replace("$", "").replace(",", "").strip()
                if (
                    plan_price.split(".")[0].isdigit()
                    and plan_price.split(".")[-1].isdigit()
                ):
                    out_row["payer"] = plan
                    out_row["price"] = plan_price
                    pprint(out_row)
                    csv_writer.writerow(out_row)

        out_f.close()
        h_f.write(
            'UPDATE `hospitals` SET `homepage_url` = "https://www.honorhealth.com/", `chargemaster_url` = "https://www.honorhealth.com/sites/default/files/patients-visitors/pricing-transparency.zip", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";\n'.format(
                cms_id
            )
        )

    h_f.close()


if __name__ == "__main__":
    main()
