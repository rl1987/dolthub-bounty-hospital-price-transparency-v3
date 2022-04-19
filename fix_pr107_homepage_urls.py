#!/usr/bin/python3

import sys

import doltcli as dolt
import requests


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    sql = 'SELECT `cms_certification_num`, `name`, `address`, `city`, `homepage_url` FROM `hospitals` WHERE `chargemaster_url` LIKE "%apps.para-hcfs.com%";'

    proxies = {
        "http": "http://lum-customer-c_cecd546c-zone-zone_serp:3rrzr9ft4t3k@zproxy.lum-superproxy.io:22225",
        "https": "http://lum-customer-c_cecd546c-zone-zone_serp:3rrzr9ft4t3k@zproxy.lum-superproxy.io:22225",
    }

    db = dolt.Dolt(sys.argv[1])

    print(sql)
    res = db.sql(sql, result_format="json")

    for row in res["rows"]:
        cms_certification_num = row["cms_certification_num"]
        name = row["name"]
        address = row["address"]
        city = row["city"]
        homepage_url = row["homepage_url"]

        q = "{} {} {}".format(name, address, city)

        params = {"q": q, "lum_json": "1"}

        resp = requests.get(
            "http://www.google.com/search", params=params, proxies=proxies
        )
        print(resp.url)

        json_dict = resp.json()

        if json_dict.get("organic") is None or len(json_dict.get("organic")) == 0:
            continue

        first_result = json_dict.get("organic")[0]

        link = first_result.get("link")

        if link == homepage_url:
            continue

        sql2 = 'UPDATE `hospitals` SET `homepage_url` = "{}", `last_edited_by_username` = "rl1987" WHERE `cms_certification_num` = "{}";'.format(
            link, cms_certification_num
        )
        print(sql2)

        db.sql(sql2)


if __name__ == "__main__":
    main()
