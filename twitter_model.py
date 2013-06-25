#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
from datetime import datetime, timedelta
import re
import numpy as np
import json
from etool import args

FEATURE_ORDER = ['net_density', 'node_num', 'weakly_componnet_num',
                 'edge_num', 'tweet_num', 'retweet_num',
                 #'tweet_hash_num', 'tweet_url_num','tweet_mens_num',
                 'hot_hash_tag', 'hot_url']

COUNTRY = ["Argentina", "Brazil", "Chile", "Colombia",
           "Costa Rica", "Peru", "Panama", "Mexico", "Venezuela"]


class Detector:
    def __init__(self, target_day, window_size, file_dir, result_file):
        self.target_day = target_day
        self.window_size = window_size
        self.file_dir = file_dir
        self.result = result_file

    def load_files(self):
        tmp_date = datetime.strptime(self.target_day, "%Y-%m-%d")
        days = []
        for i in range(self.window_size + 1):
            days.append((tmp_date + timedelta(days=-i)).strftime("%Y-%m-%d"))
        file_temp = "tweet_finance_analysis_%s"
        day_files = [os.path.join(self.file_dir,
                                  file_temp % d) for d in days]
        self.analysis = [self.read_analysis(f) for f in day_files
                         if os.path.exists(f)]

    def read_analysis(self, ana_file):
        g_date = re.search(r'\d{4}-\d{2}-\d{2}', ana_file).group()
        analysis = []
        with open(ana_file) as f:
            analysis = [json.loads(r) for r in f]
        return (g_date, analysis)

    def process(self, country):
        #transfer dict to vector
        c_matrix = []
        for day_info in self.analysis:
            for country_data in day_info[1]:
                if country_data["country"] == country:
                    vec = []
                    for k in FEATURE_ORDER:
                        vec.append(country_data[k])
                    c_matrix.append(vec)
        c_matrix = np.array(c_matrix, dtype='f2')

        #normalize the feature
        c_max = c_matrix.max(axis=0)
        c_min = c_matrix.min(axis=0)
#        print "c_max", c_max
#        print "c_min", c_min
#        print "c_matrix", c_matrix
        c_matrix = (c_matrix - c_min) / (c_max - c_min)
        #transfer the matrix to unit matrix
        c_matrix = trans2unit(c_matrix)
        tar_v = c_matrix[0]
        past_v = c_matrix[1:].sum(axis=0) / c_matrix[1:].shape[0]
        z = compare_similarity(tar_v, past_v)
        return z

    def detect(self):
        for country in COUNTRY:
            tf = self.result + "_" + country.replace(" ", "")
            z = self.process(country)
            with open(tf, "a") as w:
                r_str = "%s|%s|%0.4f\n" % (self.target_day, country, z)
                w.write(r_str)


def trans2unit(c_matrix):
    #take as row vector
    root_sqr_sum_row = (c_matrix ** 2).sum(axis=1) ** .5
    c_matrix = ((c_matrix).T / root_sqr_sum_row).T
    return c_matrix


def compare_similarity(tar_v, past_v):
    #z = 1 - tar_v * past_v', if tart_v and past_v is the same
    #then z = 0 and the higher z means hihger difference
    z = 1 - np.dot(tar_v, past_v)
    return z


def date_seed(start_date, end_date):
    base = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    duration = (end - base).days
    dates = [(base + timedelta(days=i)).strftime("%Y-%m-%d")
             for i in range(0, duration + 1)]
    return dates


def main():
    ap = args.get_parser()
    ap.add_argument('--filedir', type=str, help="analysis files")
    ap.add_argument('--window', type=int, default=7)
    ap.add_argument('--result', type=str, help="result")
    arg = ap.parse_args()

    start_date = "2012-12-08"
    end_date = "2013-02-28"
    dates = date_seed(start_date, end_date)
    for d in dates:
        detector = Detector(d, arg.window, arg.filedir, arg.result)
        detector.load_files()
        detector.detect()

if __name__ == "__main__":
    main()
