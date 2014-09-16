#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"


import pandas as pd
import sys
import os
import re
import json


def compute_dominant(cluster_file):
    if cluster_file[-1] == "/":
        single_f = cluster_file.split("/")[-2]
    else:
        single_f = cluster_file.split("/")[-1]

    day = re.search(r'\d{4}-\d{2}-\d{2}', cluster_file).group()
    country = single_f.split("_")[0]

    #compute the stable index
    """"
    stable_index = (SD * IN_CLUS_CORR) / (OUT_CLUS_CORR)
    """
    index = []
    with open(cluster_file) as cf:
        for line in cf:
            info = json.loads(line)
            stable_index = info["in_aver_corr"] * \
                info["in_aver_var"] / info["out_aver_corr"]
            index.append(stable_index)

    index.sort(reverse=True)
    print len(index)
    return country, day, [pd.np.log(pd.np.mean(index))]


def handle_dir(in_dir, out_dir):
    files = os.listdir(in_dir)
    stable_index = {}
    for f in files:
        full_f = os.path.join(in_dir, f)
        country, day, index = compute_dominant(full_f)
        for i, top in enumerate(index):
            c_name = "top_%d" % i
            if c_name not in stable_index:
                stable_index[c_name] = {}
            stable_index[c_name][day] = top
        print f
    series = pd.DataFrame(stable_index)
    series.name = "Stable_Index"
    out_file = os.path.join(out_dir, "%s_stable_index" % country)
    series.to_csv(out_file, header=True, index_label="Date")


def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    handle_dir(in_dir, out_dir)


if __name__ == "__main__":
    main()
