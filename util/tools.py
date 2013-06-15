#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
import random
import codecs
import auto_translate as at
import json


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
