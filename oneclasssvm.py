#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sqlite3 as lite
from datetime import datetime, timedelta
import json
import numpy as np
from sklearn import svm
import os


COUNTRY = ['Argentina', 'Brazil', 'Chile', 'Colombia',
           'Costa Rica', 'Mexico', 'Panama', 'Peru',
           'Venezuela']

FEATURE_ORDER = ['edge_num', 'node_num', 'net_density', 'hot_url',
                 'hot_hash_tag', 'tweet_num', 'weakly_componnet_num',
                 'retweet_num']

CONTENT_FEATURE_ORDER = ['tweet_num', 'retweet_num', 'mention_num',
                         'density', 'component_num', 'top_url',
                         'top_person', 'top_product', 'top_location',
                         'top_hashtag', 'top_organization', 'top_nation']


def filter_regular_day(country, lag=1):
    conn = lite.connect('/home/vic/work/data/embers_v.db')
    sql = "select event_date from gsr_event where event_code"
    sql += " in ('0411', '0412') and "
    sql += " country = '%s' and event_date >= '2012-12-01' " % country
    cursor = conn.cursor()
    rs = cursor.execute(sql)
    days = [r[0] for r in rs]
    lag_days = [(datetime.strptime(d, "%Y-%m-%d") -
                 timedelta(days=lag)).strftime("%Y-%m-%d")
                for d in days]
    return lag_days


def get_previous_feature(country, day, max_lag=10):
    count = 1
    day = datetime.strptime(day, "%Y-%m-%d")
    features = []
    while count < max_lag:
        day_str = (day - timedelta(days=count)).strftime("%Y-%m-%d")
        g_file = "/media/2488-4033/data/graph_analysis/tweet_finance_analysis_%s" % day_str
        if os.path.exists(g_file):
            with open(g_file, "r") as r:
                ds = [json.loads(l) for l in r]
                for d in ds:
                    if d["country"] == country:
                        features = [d[k] for k in FEATURE_ORDER]
            break
        count += 1
    return features


def compute_diff(last, curr):
    def get_return(x, y):
        if y == .0:
            return 0.0
        return (x - y) / float(y)

    diff = [get_return(curr[i], last[i]) for i in range(len(last))]
    return diff


def construct_dataset(country, lag=1):
    s_train_date = "2012-12-15"
    e_train_date = "2013-05-01"
    anomaly_days = filter_regular_day(country, lag)
    regular_days = []
    temp_s_date = datetime.strptime(s_train_date, "%Y-%m-%d")
    temp_e_date = datetime.strptime(e_train_date, "%Y-%m-%d")
    while temp_s_date < temp_e_date:
        if temp_s_date.strftime("%Y-%m-%d") not in anomaly_days:
            regular_days.append(temp_s_date.strftime("%Y-%m-%d"))
        temp_s_date += timedelta(days=1)

    print "Country: %s Traning Regular days: %d, Anormaly days: %d" \
        % (country, len(regular_days), len(anomaly_days))
    datas = []
    #generate training dataset
    for d in regular_days:
        g_file = "/media/2488-4033/data/graph_analysis/tweet_finance_analysis_%s" % d
        try:
            with open(g_file, "r") as r:
                for l in r:
                    data = json.loads(l)
                    if country == data["country"]:
                        #extract information
                        tmd = [data[k] for k in FEATURE_ORDER]
                        p_feature = get_previous_feature(country, d)
                        diff = compute_diff(p_feature, tmd)
                        datas.append(diff)
        except:
            continue

    #generate test dataset
    test_datas = []
    test_days = []
    test_start = "2013-05-01"
    test_end = "2013-07-31"

    temp_s_date = datetime.strptime(test_start, "%Y-%m-%d")
    temp_e_date = datetime.strptime(test_end, "%Y-%m-%d")
    while temp_s_date <= temp_e_date:
        d_str = temp_s_date.strftime("%Y-%m-%d")
        g_file = "/media/2488-4033/data/graph_analysis/tweet_finance_analysis_%s" % d_str
        temp_s_date += timedelta(days=1)
        try:
            with open(g_file, "r") as r:
                for l in r:
                    data = json.loads(l)
                    if country == data["country"]:
                        tmd = [data[k] for k in FEATURE_ORDER]
                        p_feature = get_previous_feature(country, d_str)
                        diff = compute_diff(p_feature, tmd)
                        test_datas.append(diff)
                        test_days.append(data["date"])
        except Exception:
            continue

    return np.array(datas), np.array(test_datas), np.array(test_days)


def model_test():
    for country in COUNTRY:
        train, test, test_days = construct_dataset(country, 1)

        #normalize data
        mean = train.mean(axis=0)
        std = train.std(axis=0)
        norm_train = (train - mean) / std
        norm_test = (test - mean) / std

        clf = svm.OneClassSVM(nu=0.1, kernel='rbf', gamma=0.125)
        clf.fit(norm_train)

        #evaluation
        test_pred = clf.predict(norm_test)
        num_anor = test_pred[test_pred == -1].size

        print "Country: %s , total: %d, anorm: %d, ratio: %0.4f" \
            % (country, test_pred.size, num_anor,
               1.0 * num_anor / test_pred.size)
        print "anomaly days:", test_days[test_pred == -1]
        print "\n"


if __name__ == "__main__":
    model_test()
