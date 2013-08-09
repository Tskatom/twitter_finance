#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
import sqlite3 as lite
from datetime import datetime
import random
import codecs
import auto_translate as at
import json
import re
import numpy as np


INDEX_COUNTRY = {"MERVAL": "Argentina", "IBOV": "Brazil",
                 "CHILE65": "Chile", "COLCAP": "Colombia",
                 "CRSMBCT": "Costa Rica", "IGBVL": "Peru",
                 "IBVC": "Venezuela", "BVPSBVPS": "Panama",
                 "MEXBOL": "Mexico"}


def group_user_by_country(user_file):
    user_group = {"others": []}
    rules = {"CostaRica": ["Costa Rica"], "Argentina": ["Argentina"],
             "Brazil": ["Brazil", "Brasil"], "Mexico": ["Mexico", "México"],
             "Chile": ["Chile"], "Colombia": ["Colombia"],
             "Panama": ["Panama", "Panamá"], "Venezuela": ["Venezuela"],
             "Peru": ["Peru", "Perú"]}

    country_rule = {}
    for country in rules:
        country_rule[country] = "(" + '|'.join(rules[country]) + ")"
    with codecs.open(user_file) as uf:
        for l in uf:
            l = json.loads(l)
            location = l["location"]
            #check by country
            flag = False
            for country in country_rule:
                if re.search(country_rule[country], location):
                    flag = True
                    if country not in user_group:
                        user_group[country] = []
                    user_group[country].append(l['id_str'])
                    break
            if not flag:
                user_group["others"].append(l['id_str'])
    for country in user_group:
        c_f = country + "_users.txt"
        with codecs.open(c_f, 'w') as cfw:
            for _id in user_group[country]:
                cfw.write("%s\n" % _id)


def random_sample_users(user_file, out_file, num):
    users = []
    with codecs.open(user_file) as uf:
        for user in uf.readlines():
            user = json.loads(user)
            name = user['screen_name']
            desc = user['description']
            users.append("%s|%s" % (name, desc))
    sampled = random.sample(users, num)

    with codecs.open(out_file, "w") as uw:
        for user in sampled:
            uw.write(user.encode('utf-8') + "\n")

    un = os.environ['NOTIFIER']
    pw = os.environ['NOTIFIER_PWD']
    translator = at.Translator(un, pw)

    translator.get_workspace()
    translator.clear_sheet()
    result = translator.translate_file(out_file, "es", "en")
    return result


def extract_users(tweet_file, user_file):
    users = []
    with codecs.open(tweet_file, "r") as tf, \
            codecs.open(user_file, "w") as uf:
        for line in tf:
            tweet = json.loads(line)
            user = tweet.get("user", None)
            if user:
                if user['screen_name'] not in users:
                    users.append(user['screen_name'])
                    uf.write(json.dumps(
                        user,
                        ensure_ascii=False).encode('utf-8') + "\n")
                if "retweeted_status" in tweet and \
                   "user" in tweet["retweeted_status"]:
                    re_user = tweet["retweeted_status"]["user"]
                    if re_user["screen_name"] not in users:
                        users.append(re_user['screen_name'])
                        uf.write(json.dumps(
                            re_user,
                            ensure_ascii=False).encode('utf-8') + "\n")

    return users


def combine_country_market(c_file, m_file, out_file, merge_file):
    country_users = json.load(open(c_file))
    market_users = json.load(open(m_file))
    users = []
    for country, us in country_users.items():
        users.extend(us)
    for market, us in market_users.items():
        users.extend(us)

    users = list(set(users))
    with open(out_file, "w") as w:
        for id in users:
            w.write(json.dumps({"id": int(id)}) + "\n")

    #merge users
    for k in country_users:
        if k in market_users:
            country_users[k].extend(market_users[k])
            country_users[k] = list(set(country_users[k]))

    with open(merge_file, "w") as w:
        w.write(json.dumps(country_users))


#input stock price and compute z30/z90
def compute_zscore(price_file):
    with open(price_file) as r:
        print price_file
        lines = [l.strip() for l in r]
        index = lines[0].split(",")[0].split(" ")[0]
        days = np.array([l.split(",")[0] for l in lines[2:]])
        day_changes = np.array([float(l.split(",")[1]) - float(l.split(",")[2]) for l in lines[2:]])
        z30s = np.zeros(len(days))
        z90s = np.zeros(len(days))
        for i in range(1, len(days)):
            end = i - 1
            start = (i - 30) if (i - 30) > 0 else 0
            mean = np.mean(day_changes[start:end])
            std = np.std(day_changes[start:end])
            z30 = (day_changes[i] - mean) / std

            start = (i - 90) if (i - 90) > 0 else 0
            mean = np.mean(day_changes[start:end])
            std = np.std(day_changes[start:end])
            z90 = (day_changes[i] - mean) / std

            z30s[i] = z30
            z90s[i] = z90

    p_z30 = days[z30s >= 4]
    n_z30 = days[z30s <= -4]
    p_z90 = days[z90s >= 3]
    n_z90 = days[z90s <= -3]


    gsr_p_events = set()
    gsr_n_events = set()
    gsr_p_events = gsr_p_events.union(p_z30)
    gsr_n_events = gsr_n_events.union(n_z30)
    gsr_p_events = gsr_p_events.union(p_z90)
    gsr_n_events = gsr_n_events.union(n_z90)

    country = INDEX_COUNTRY[index]
    gsr_p_events = list(gsr_p_events)
    gsr_n_events = list(gsr_n_events)

    gsr_p_events.sort()
    gsr_n_events.sort()

    #insert to database
    conn = lite.connect("/home/vic/workspace/data/embers_v.db")
    sql = "insert into gsr_event (event_id, country, event_code, population, event_date) values (?, ?, ?, ?, ?)"
    cur = conn.cursor()

    for i, event in enumerate(gsr_p_events):
        event_id = i + 100000
        event_date = datetime.strptime(event, "%m/%d/%Y").strftime("%Y-%m-%d")
        event_code = "0411"
        print event_date, event_id
        if event_date >= '2013-07-01':
            cur.execute(sql, [event_id, country, event_code, index, event_date])

    for i, event in enumerate(gsr_n_events):
        event_id = i + 200000
        event_date = datetime.strptime(event, "%m/%d/%Y").strftime("%Y-%m-%d")
        event_code = "0412"
        print event_date, event_id
        if event_date >= "2013-07-01":
            cur.execute(sql, [event_id, country, event_code, index, event_date])
    conn.commit()
def import_gsr_self():
    dir = "/home/vic/workspace/data/latest_stock/"
    for f in os.listdir(dir):
        f = os.path.join(dir, f)
        print f
        compute_zscore(f)

if __name__ == "__main__":
    pass
