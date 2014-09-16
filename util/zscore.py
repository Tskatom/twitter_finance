#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import pandas as pd
import numpy as np


def zscore(price_series):
    size = len(price_series)
    z30s = np.array([np.nan] * size)
    z90s = np.array([np.nan] * size)
    series = pd.Series(price_series)

    #compute z30
    for i in range(30, size):
        pre_30 = series[i - 30: i - 1]
        mean_30 = pre_30.mean()
        std = pre_30.std()

        z30 = (series[i] - mean_30) / std
        z30s[i] = z30

    #compute z90
    for i in range(90, size):
        pre_90 = series[i - 90: i - 1]
        mean_90 = pre_90.mean()
        std = pre_90.std()

        z90 = (series[i] - mean_90) / std
        z90s[i] = z90

    return z30s, z90s


def handle_price_file(price_file, out_dir):
    price_frame = pd.DataFrame.from_csv(price_file)
    change_series = price_frame.PX_LAST - price_frame.PX_CLOSE_1D
    z30s, z90s = zscore(change_series.values)

    series_z30s = pd.Series(z30s, index=change_series.index)
    series_z90s = pd.Series(z90s, index=change_series.index)

    if price_file[-1] == "/":
        index = price_file.split("/")[-2].split(".")[0]
    else:
        index = price_file.split("/")[-1].split(".")[0]

    z30_out = os.path.join(out_dir, "%s_z30" % index)
    z90_out = os.path.join(out_dir, "%s_z90" % index)

    series_z30s.name = "z30"
    series_z90s.name = "z90"

    series_z30s.to_csv(z30_out, header=True, index_label="Date")
    series_z90s.to_csv(z90_out, header=True, index_label="Date")


def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    for f in os.listdir(in_dir):
        price_file = os.path.join(in_dir, f)
        handle_price_file(price_file, out_dir)


if __name__ == "__main__":
    main()
