#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import redis
import re
import json
import os

COUNTRY = {"Panamá": "Panama", "América": "Latin America",
           "Perú": "Peru", "México": "Mexico", "Brasil": "Brazil"}


def get_user(r, keys):
    users = []
    for k in keys:
        ts = r.smembers(k)
        for t in ts:
            users.extend(extract_user(eval(t)))
    return users


def extract_user(tweet):
    ids = []
    #add author id
    if "user" in tweet:
        ids.append(tweet["user"]["id_str"])

    #add mentioned users
    for m_user in tweet["entities"]["user_mentions"]:
        ids.append(m_user["id_str"])

    #add original user
    if "retweeted_status" in tweet:
        if "user" in tweet["retweeted_status"]:
            ids.append(tweet["retweeted_status"]["user"]["id_str"])

    return ids


def extract(flag="country"):
    r = redis.Redis()
    keys = r.keys()
    #divide the country into two groups: costa rica and others
    costa = [k for k in keys if re.search('costa', k, re.IGNORECASE)]
    others = [k for k in keys if re.search('costa', k, re.IGNORECASE) is None]

    users = {}
    cost_users = get_user(r, costa)
    users["Costa Rica"] = cost_users

    #get other countr's users
    other_country = {}
    for k in others:
        country = country_trans(k.split(" ")[0])
        if country not in other_country:
            other_country[country] = []
        other_country[country].append(k)

    for country, rule in other_country.items():
        users[country] = get_user(r, rule)

    for u in users:
        users[u] = list(set(users[u]))

    user_file = "/home/vic/workspace/twitter_finance/dictionary/"
    if not os.path.exists(user_file):
        user_file = "/home/vic/work/twitter_finance/dictionary/"
    if flag == "country":
        user_file += "eco_user_by_country.txt"
    elif flag == "market":
        user_file += "eco_user_by_market.txt"
    with open(user_file, "w") as w:
        w.write(json.dumps(users))

    return users


def country_trans(country):
    if country in COUNTRY:
        return COUNTRY[country]
    else:
        return country


if __name__ == "__main__":
    pass
