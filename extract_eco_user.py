#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import codecs
import json

USERS = {}


def extract_file(tweet_file, user_file):
    with codecs.open(tweet_file) as tf:
        for line in tf.readlines():
            tweet = json.loads(line)
            user = tweet.get("user", None)
            if user is None:
                continue
            screen_name = user["screen_name"]
            if screen_name in USERS:
                continue
            else:
                USERS[screen_name] = 1
            user_file.write(
                json.dumps(user,
                           ensure_ascii=False).encode('utf-8') + "\n")
    user_file.flush()


def process():
    file_list = []
    u_file = "/home/vic/work/twitter_finance/dictionary/eco_users.txt"
    user_file = codecs.open(u_file, "w")
    for tf in file_list:
        extract_file(tf, user_file)
        print "Done %s" % tf

    user_file.close()

if __name__ == "__main__":
    pass
