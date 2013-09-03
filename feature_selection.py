#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
import sqlite3 as lite
from dateutil import parser
from datetime import timedelta
import re
import json
import numpy as np
"""
For each featue, choose the regular value and the exception value,
apply the algorithm that F=((mean(pos) - mean(x))**2 +
(mean(neg) - meanx(x))**2)/(variance(pos) + variance(neg) )
"""

RULE = {"t": "content", "u": "user2user", "c": "comprehend"}
COUNTRY = ["Argentina", "Brazil", "Chile", "Colombia",
           "Costa Rica", "Mexico", "Panama", "Peru",
           "Venezuela"]

def find_novel_days(country, start, end, lag):
    conn = lite.connect("/home/vic/work/data/embers_v.db")
    sql = "select event_date from gsr_event where event_code "
    sql += " in ('0411', '0412') and "
    sql += " country='%s' and event_date >= '%s' and event_date <= '%s' " \
        % (country, start, end)
    cur = conn.cursor()
    rs = cur.execute(sql)
    days = [r[0] for r in rs]
    novel_days = [(parser.parse(d) - timedelta(days=lag)).strftime("%Y-%m-%d")
                  for d in days]
    return novel_days


def compute_f1(country, start, end, net, lag):
    novel_days = find_novel_days(country, start, end, lag)
    basic_dir = "/media/datastorage/graph_analysis"
    dir = os.path.join(basic_dir, RULE[net])
    files = os.listdir(dir)
    positive = {}
    all = {}
    negative = {}
    all_days = set()
    p_days = set()

    for f in files:
        full_f = os.path.join(dir, f)
        if not os.path.isfile(full_f):
            continue
        date = re.search(r'(\d{4}-\d{2}-\d{2})', f).group()
        for l in open(full_f):
            features = json.loads(l)
            cy = features["country"]
            if country == cy:
                for fea in features:
                    if (fea != "country") and (fea != "date"):
                        if fea not in all:
                            all[fea] = []
                        all_days.add(date)
                        all[fea].append(float(features[fea]))
                        if date in novel_days:
                            if fea not in negative:
                                negative[fea] = []
                            negative[fea].append(float(features[fea]))
                        else:
                            p_days.add(date)
                            if fea not in positive:
                                positive[fea] = []
                            positive[fea].append(float(features[fea]))

    #computre
    neg_summary = {k: np.mean(v) for k, v in negative.items()}
    pos_summary = {k: np.mean(v) for k, v in positive.items()}
    all_summary = {k: np.mean(v) for k, v in all.items()}
    scores = []
    for key in all.keys():
        p_term = (pos_summary[key] - all_summary[key]) ** 2
        n_term = (neg_summary[key] - all_summary[key]) ** 2
        p_var = np.std(positive[key], ddof=1) ** 2
        n_var = np.std(negative[key], ddof=1) ** 2
        f1_score = (p_term + n_term) / (p_var + n_var)
        scores.append((key, f1_score))

    scores.sort(key=lambda x: x[1], reverse=True)
    print country, scores
    return scores


def filter_feature(k=7, lag=1):
    start = "2012-12-01"
    end = "2013-07-31"
    net = "t"
    for country in COUNTRY:
        scores = compute_f1(country, start, end, net, lag)
        print "\n"


if __name__ == "__main__":
    pass
