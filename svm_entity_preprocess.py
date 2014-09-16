#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import pandas as pd
import sqlite3 as lite
from dateutil import parser
from datetime import timedelta


COUNTRY_INDEX = {"Argentina": "MERVAL", "Brazil": "IBOV",
                 "Chile": "Chile65", "Colombia": "COLCAP",
                 "CostaRica": "CRSMBCT", "Mexico": "MEXBOL",
                 "Peru": "IGBVL", "Panama": "BVPSBVPS", "Venezuela": "IBVC"}


def construct_set(dominant_file, country,
                  train_start, train_end,
                  test_start, test_end, out_dir):
    stock = COUNTRY_INDEX[country]

    conn = lite.connect("/home/vic/work/data/embers_v.db")
    sql = "select event_date from gsr_event where "
    sql += " population='%s' and event_date >= '%s' and event_date <= '%s' " % (stock,
                                                                                train_start,
                                                                                train_end)
    cur = conn.cursor()
    cur.execute(sql)
    rs = cur.fetchall()
    event_days = [parser.parse(r[0]) for r in rs]
    critical_days = [d - timedelta(days=1) for d in event_days]

    s_index_frame = pd.DataFrame.from_csv(dominant_file)
    # get the normal days for training
    normal_days = sorted(list(set(s_index_frame[train_start:train_end].index).difference(critical_days)))
    train_data = s_index_frame[train_start: train_end].ix[normal_days]
    test_data = s_index_frame[test_start: test_end]

    #save to file
    out_train = os.path.join(out_dir, "%s_train_1" % country)
    out_test = os.path.join(out_dir, "%s_test_1" % country)

    train_data.to_csv(out_train, sep=' ', header=False)
    test_data.to_csv(out_test, sep=' ', header=False)


def handle_dir(in_dir, out_dir):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    files = os.listdir(in_dir)
    train_start = "2013-01-01"
    train_end = "2013-05-31"
    test_start = "2013-06-01"
    test_end = "2013-07-31"

    for f in files:
        full_f = os.path.join(in_dir, f)
        country = f.split("_")[0]
        construct_set(full_f, country, train_start, train_end, test_start, test_end, out_dir)


def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]
    for dir in os.listdir(in_dir):
        new_out_dir = os.path.join(out_dir, dir)
        new_in_dir = os.path.join(in_dir, dir)
        handle_dir(new_in_dir, new_out_dir)


if __name__ == "__main__":
    main()
