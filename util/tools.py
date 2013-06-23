#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
import random
import codecs
import auto_translate as at
import json
import re


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

if __name__ == "__main__":
    pass
