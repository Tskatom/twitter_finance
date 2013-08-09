#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sqlite3 as lite
from datetime import datetime, timedelta
import json
import numpy as np
import os
import argparse


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

RULE = {"t": "content", "c": "comprehend", "u": "user2user"}
ORDER_RULE = {"t": CONTENT_FEATURE_ORDER, "c": FEATURE_ORDER}


def filter_regular_day(country, train_start, train_end, lag=1):
    conn = lite.connect('/home/vic/work/data/embers_v.db')
    sql = "select event_date from gsr_event where event_code"
    sql += " in ('0411', '0412') and "
    sql += " country = '%s' and event_date >= '%s'  and event_date < '%s'" % (country, train_start, train_end)
    cursor = conn.cursor()
    rs = cursor.execute(sql)
    days = [r[0] for r in rs]
    lag_days = [(datetime.strptime(d, "%Y-%m-%d") -
                 timedelta(days=lag)).strftime("%Y-%m-%d")
                for d in days]
    return lag_days


def get_previous_feature(country, day, net_type, max_lag=10):
    path = "/media/datastorage/graph_analysis/" + RULE[net_type] + "/tweet_finance_analysis_%s"
    count = 1
    day = datetime.strptime(day, "%Y-%m-%d")
    features = []
    while count < max_lag:
        day_str = (day - timedelta(days=count)).strftime("%Y-%m-%d")
        g_file = path % day_str
        if os.path.exists(g_file):
            with open(g_file, "r") as r:
                ds = [json.loads(l) for l in r]
                for d in ds:
                    if d["country"] == country:
                        features = [d[k] for k in ORDER_RULE[net_type]]
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


def construct_dataset(country, train_start, train_end, test_start, test_end, net_type, lag=1):
    path = "/media/datastorage/graph_analysis/" + RULE[net_type] + "/tweet_finance_analysis_%s"
    s_train_date = train_start
    e_train_date = train_end
    anomaly_days = filter_regular_day(country, train_start, train_end, lag)
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
    train_days = []
    #generate training dataset
    for d in regular_days:
        g_file = path % d
        try:
            with open(g_file, "r") as r:
                for l in r:
                    data = json.loads(l)
                    if country == data["country"]:
                        #extract information
                        tmd = [data[k] for k in ORDER_RULE[net_type]]
                        p_feature = get_previous_feature(country, d, net_type)
                        diff = compute_diff(p_feature, tmd)
                        datas.append(diff)
                        train_days.append(d)
        except:
            continue

    #generate test dataset
    test_datas = []
    test_days = []
    test_start = test_start
    test_end = test_end

    temp_s_date = datetime.strptime(test_start, "%Y-%m-%d")
    temp_e_date = datetime.strptime(test_end, "%Y-%m-%d")
    while temp_s_date <= temp_e_date:
        d_str = temp_s_date.strftime("%Y-%m-%d")
        g_file = path % d_str
        temp_s_date += timedelta(days=1)
        try:
            with open(g_file, "r") as r:
                for l in r:
                    data = json.loads(l)
                    if country == data["country"]:
                        tmd = [data[k] for k in ORDER_RULE[net_type]]
                        p_feature = get_previous_feature(country, d_str, net_type)
                        diff = compute_diff(p_feature, tmd)
                        test_datas.append(diff)
                        test_days.append(data["date"])
        except Exception:
            continue

    return np.array(train_days), np.array(datas), np.array(test_datas), np.array(test_days)


def parse_arg():
    ap = argparse.ArgumentParser()
    ap.add_argument("--net", type=str)
    ap.add_argument("--train_start", type=str)
    ap.add_argument("--train_end", type=str)
    ap.add_argument("--test_start", type=str)
    ap.add_argument("--test_end", type=str)
    ap.add_argument("--lag", type=int)
    return ap.parse_args()


def main():
    arg = parse_arg()
    for country in COUNTRY:
        train_days, train_data, test_data, test_days = construct_dataset(country,
                                                                         arg.train_start,
                                                                         arg.train_end,
                                                                         arg.test_start,
                                                                         arg.test_end,
                                                                         arg.net,
                                                                         arg.lag)
        #output ot file
        train_file = "/media/datastorage/experiment/" + RULE[arg.net]
        train_file += "/%s_train" % country.replace(" ", "")

        test_file = "/media/datastorage/experiment/" + RULE[arg.net]
        test_file += "/%s_test" % country.replace(" ", "")


        with open(train_file, "w") as train, open(test_file, "w") as test:
            for i in range(1, len(train_days)):
                t_str = train_days[i] + " "
                t_str += " ".join(map(str, train_data[i])) + "\n"
                train.write(t_str)

            for i in range(len(test_days)):
                t_str = test_days[i] + " "
                t_str += " ".join(map(str, test_data[i])) + "\n"
                test.write(t_str)


if __name__ == "__main__":
    main()
