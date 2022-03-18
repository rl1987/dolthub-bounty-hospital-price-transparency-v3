#!/usr/bin/python3

import csv
from pprint import pprint
import sys
import os
import shutil
import uuid

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


def set_code_disambiguator(csv_file_path):
    print("###############################################################################")
    print(csv_file_path)
    print("###############################################################################")
        
    uuid_dict = dict()
    code_counts = dict()
    comb_counts = dict()

    tmp_path1 = "pass1_" + csv_file_path
    tmp_path2 = "pass2_" + csv_file_path

    in1_f = open(csv_file_path, "r", encoding="utf-8")
    out1_f = open(tmp_path1, "w", encoding="utf-8")

    csv_reader1 = csv.DictReader(in1_f)
    csv_writer1 = csv.DictWriter(out1_f, fieldnames=FIELDNAMES, lineterminator='\n')
    csv_writer1.writeheader()

    for in_row in csv_reader1:
        #code_disambiguator = in_row.get('code_disambiguator')
        #if code_disambiguator != "" and code_disambiguator != "NONE":
        #    continue

        cms_certification_num = in_row.get('cms_certification_num')
        payer = in_row.get('payer')
        code = in_row.get('code')
        internal_revenue_code = in_row.get('internal_revenue_code')
        inpatient_outpatient = in_row.get('inpatient_outpatient')
        price = in_row.get("price")
    
        k = (cms_certification_num, payer, code, internal_revenue_code, inpatient_outpatient, price)

        if uuid_dict.get(k) is not None:
            continue

        v = str(uuid.uuid4())
        uuid_dict[k] = v

        if code_counts.get(code) is None:
            code_counts[code] = 1
        else:
            code_counts[code] += 1

        comb = (cms_certification_num, payer, code, internal_revenue_code, inpatient_outpatient)
        
        if comb_counts.get(comb) is None:
            comb_counts[comb] = 1
        else:
            comb_counts[comb] += 1

        out_row = dict(in_row)

        out_row['code_disambiguator'] = v
        
        csv_writer1.writerow(out_row)

    pprint(uuid_dict)
    pprint(code_counts)
    pprint(comb_counts)

    in1_f.close()
    out1_f.close()
 
    codes = list(code_counts.keys())
    for c in codes:
        if code_counts[c] == 1:
            del code_counts[c]

    in2_f = open(tmp_path1, "r", encoding="utf-8")
    out2_f = open(tmp_path2, "w", encoding="utf-8")

    csv_reader2 = csv.DictReader(in2_f)
    csv_writer2 = csv.DictWriter(out2_f, fieldnames=FIELDNAMES, lineterminator="\n")
    csv_writer2.writeheader()

    uuid_to_idx = dict()

    for k in uuid_dict.keys():
        code = k[2]
        u = uuid_dict[k]

        n = code_counts.get(code)
        if n is None:
            continue
        
        uuid_to_idx[u] = n
        code_counts[code] -= 1

    pprint(uuid_to_idx)

    for in_row in csv_reader2:
        out_row = dict(in_row)

        code_disambiguator = in_row.get('code_disambiguator')

        cms_certification_num = in_row.get('cms_certification_num')
        payer = in_row.get('payer')
        code = in_row.get('code')
        internal_revenue_code = in_row.get('internal_revenue_code')
        inpatient_outpatient = in_row.get('inpatient_outpatient')
        
        comb = (cms_certification_num, payer, code, internal_revenue_code, inpatient_outpatient)
        
        if comb_counts.get(comb) == 1:
            out_row['code_disambiguator'] = "NONE"
        else:
            idx = uuid_to_idx.get(code_disambiguator)
            if idx is not None:
                out_row['code_disambiguator'] = idx
            else:
                out_row['code_disambiguator'] = "NONE"

        csv_writer2.writerow(out_row)

    in2_f.close()
    out2_f.close()

    shutil.move(tmp_path2, csv_file_path)
    os.unlink(tmp_path1)

def main():
    if len(sys.argv) == 1:
        print("{} <csv_file...>".format(sys.argv[0]))
        return

    for csv_file_path in sys.argv[1:]:
        set_code_disambiguator(csv_file_path)

if __name__ == "__main__":
    main()
