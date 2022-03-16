#!/usr/bin/python3

import csv
from pprint import pprint
import sys

import doltcli as dolt

FIELDNAMES = ["cdm_url", "ccn", "web_url"]

OVERRIDES = {
    "https://www.tennovanorthknoxville.com/Uploads/Public/Documents/charge-masters/452535623_Tennova%20North%20Knoxville_standardcharges.csv": "440120",
    "https://www.tennovacleveland.com/Uploads/Public/Documents/charge-masters/621281627_Tennova%20Cleveland_standardcharges.csv": "440185",
    "https://www.nwhealthstarke.com/Uploads/Public/Documents/charge-masters/272691760_Starke_standardcharges.csv": "150102",
    "https://www.nwhealthporter.com/Uploads/Public/Documents/charge-masters/208473972_Porter_standardcharges.csv": "150035",
    "https://www.lutherandowntownhospital.com/Uploads/Public/Documents/charge-masters/510382045_St%20Joseph_standardcharges.csv": "150047",
    "https://www.lutheranhospital.com/Uploads/Public/Documents/charge-masters/351963748_Lutheran_standardcharges.csv": "150017",
    "https://www.nwhealthlaporte.com/Uploads/Public/Documents/charge-masters/810722737_LaPorte_standardcharges.csv": "150006",
    "https://www.theduponthospital.com/Uploads/Public/Documents/charge-masters/621801445_Dupont_standardcharges.csv": "150150",
    "https://www.physiciansregional.com/Uploads/Public/Documents/charge-masters/204401957_Physicians%20Regional%20Pine%20Ridge_standardcharges.csv": "100286",
    "https://www.healthiertucson.com/Uploads/Public/Documents/charge-masters/522379881_NW%20Oro%20Valley_standardcharges.csv": "030114",
    "https://www.healthiertucson.com/Uploads/Public/Documents/charge-masters/621762430_NW%20Tucson_standardcharges.csv": "030085",
    "https://www.merithealthwomanshospital.com/Uploads/Public/Documents/charge-masters/640780035_Merit%20Woman's_standardcharges.csv": "250136",
}


def write_output_row(csv_writer, cdm_url, ccn, web_url):
    row = {"cdm_url": cdm_url, "ccn": ccn, "web_url": web_url}
    pprint(row)
    csv_writer.writerow(row)


def main():
    in_f = open("cdm_urls.csv", "r")
    csv_reader = csv.DictReader(in_f)

    out_f = open("ccn.csv", "w", encoding="utf-8")
    csv_writer = csv.DictWriter(out_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer.writeheader()

    seen_cdm_urls = set()

    if len(sys.argv) == 2:
        db = dolt.Dolt(sys.argv[1])
    else:
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    for in_row in csv_reader:
        web_url = in_row.get("web_url")
        cdm_url = in_row.get("cdm_url")
        if cdm_url in seen_cdm_urls:
            continue

        seen_cdm_urls.add(cdm_url)

        if OVERRIDES.get(cdm_url) is not None:
            ccn = OVERRIDES.get(cdm_url)
            write_output_row(csv_writer, cdm_url, ccn, web_url)
            continue

        phone_number = (
            in_row.get("phone")
            .replace(")", "")
            .replace(" ", "")
            .replace("-", "")
            .replace(")", "")
        )

        if phone_number != "":
            res = db.sql(
                'SELECT `cms_certification_num` FROM `hospitals` WHERE `phone_number` = "{}";'.format(
                    phone_number
                ),
                result_format="json",
            )

            if len(res["rows"]) == 1:
                write_output_row(
                    csv_writer,
                    res["rows"][0]["cms_certification_num"],
                    cdm_url,
                    web_url,
                )
                continue

        street_addr = in_row.get("street_addr")
        state = in_row.get("state")
        zipcode = in_row.get("zipcode")

        res = db.sql(
            'SELECT `cms_certification_num` FROM `hospitals` WHERE `address` LIKE "%{}%" AND `state` LIKE "{}" and `zip5` LIKE "{}";'.format(
                street_addr.replace("-", "").replace(".", ""), state, zipcode
            ),
            result_format="json",
        )

        if len(res["rows"]) == 1:
            write_output_row(
                csv_writer, cdm_url, res["rows"][0]["cms_certification_num"], web_url
            )
            continue

        name = in_row.get("name")

        res = db.sql(
            'SELECT `cms_certification_num` FROM `hospitals` WHERE `name` LIKE "%{}%";'.format(
                name.strip()
            ),
            result_format="json",
        )
        if len(res["rows"]) == 1:
            write_output_row(
                csv_writer, cdm_url, res["rows"][0]["cms_certification_num"], web_url
            )
            continue

        print("Found no matching CCN for:")
        pprint(in_row)

    in_f.close()
    out_f.close()


if __name__ == "__main__":
    main()
