#!/usr/bin/python3

import sys

import doltcli as dolt


def main():
    if len(sys.argv) == 2:
        db = dolt.Dolt(sys.argv[1])
    else:
        print("{} <dolt_db_dir>".format(sys.argv[0]))
        return

    sql1 = (
        "SELECT COUNT(*) FROM `hospitals` WHERE `last_edited_by_username` IS NOT NULL;"
    )
    print(sql1)

    res = db.sql(sql1, result_format="json")

    n = res["rows"][0]["COUNT(*)"]

    if n < 1500:
        multiplier = 1
    else:
        multiplier = 1500 / n

    sql2 = "SELECT `last_edited_by_username`, COUNT(*) FROM `hospitals` WHERE `last_edited_by_username` IS NOT NULL GROUP BY `last_edited_by_username` ORDER BY `count(*)` DESC"
    print(sql2)

    res = db.sql(sql2, result_format="json")

    for row in res["rows"]:
        name = row["last_edited_by_username"]
        count = row["COUNT(*)"]
        winnings = 10 * multiplier * count

        print(name, count, "$" + str(winnings))


if __name__ == "__main__":
    main()
