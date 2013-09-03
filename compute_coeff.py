#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import pandas as pd


def compute_corr(matrix_file, out_dir):
    if matrix_file[-1] == "/":
        matrix_file = matrix_file[0:len(matrix_file) - 1]

    df = pd.DataFrame().from_csv(matrix_file)
    #filter the entity less than 10
    sum_d = df.sum(axis=0)
    df = df[sum_d[sum_d >= 10.0].index]
    df_corr = df.corr()

    out_file = os.path.join(out_dir, "%s_corr" % matrix_file.split("/")[-1])
    df_corr.to_csv(out_file, index_lable="entity", header=True)


def handle_dir(in_dir, out_dir):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    error_log = open("/media/datastorage/error/compute_coeff.log", "w")

    for f in os.listdir(in_dir):
        full_f = os.path.join(in_dir, f)
        try:
            compute_corr(full_f, out_dir)
        except:
            error_log.write(full_f)
        print "Finish %s" % f
    error_log.flush()
    error_log.close()


def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    handle_dir(in_dir, out_dir)

if __name__ == "__main__":
    main()
