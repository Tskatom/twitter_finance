#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"


import pandas as pd
import re
from dateutil.parser import parse
from datetime import timedelta
import os
import sys


def create_matrix(tweet_file, out_dir):
    """
    construct a word date dictinary
    """
    current_day = re.search(r"\d{4}-\d{2}-\d{2}", tweet_file).group()
    start_time = (parse(current_day) - timedelta(days=1)).strftime("%Y-%m-%d")
    start_time += "T23"
    #the data only available from previous 22 to current day 22
    tf = open(tweet_file, "r")
    word_hour = {}
    for line in tf:
        info = line.strip().split("\t")
        try:
            t_stamp = info[0]
            word = info[1]
            count = float(info[2])
            if t_stamp < start_time:
                continue
            if word not in word_hour:
                word_hour[word] = {}
            word_hour[word][t_stamp] = count
        except:
            continue

    #transfer the dic into a dataframe
    if tweet_file[-1] == "/" or tweet_file[-1] == "\\":
        tweet_file = tweet_file[0:len(tweet_file) - 1]

    out_file = os.path.join(out_dir, "%s_matrix" % tweet_file.split("/")[-1])
    print out_file
    pd.DataFrame(word_hour).fillna(0).to_csv(out_file,
                                             index_label="date",
                                             header=True)


def handle_dir(in_dir, out_dir):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    for f in os.listdir(in_dir):
        full_f = os.path.join(in_dir, f)
        create_matrix(full_f, out_dir)
        print "Finish: %s \n" % f


def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    handle_dir(in_dir, out_dir)


if __name__ == "__main__":
    main()
