#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
from collections import Counter
import json
import codecs
import unicodedata
import sys


def normalize_str(s, lower=True):
    if isinstance(s, str):
        s = s.decode("utf8")
        s = unicodedata.normalize("NFKD", s)
        if lower:
            return s.encode('ASCII', 'ignore').lower()
        else:
            return s.encode('ASCII', 'ignore')


def extract_entity(tweet_file, out_dir):
    if tweet_file[-1] == "/" or tweet_file[-1] == "\\":
        tweet_file = tweet_file[0:len(tweet_file) - 1]

    day_entities = []
    with codecs.open(tweet_file, encoding="utf8") as tf:
        for l in tf:
            try:
                tweet = json.loads(l)
                date_stamp = tweet["date"][:13]
                for t in tweet["BasisEnrichment"]["entities"]:
                    day_entities.append("%s_%s" % (date_stamp,
                                                   t["expr"].strip().lower()))
            except:
                print "Error: %s" % l
                continue

    entities = Counter(day_entities)

    #store the entity in file
    sort_keys = sorted(entities.keys())
    out_file = os.path.join(out_dir, tweet_file.split("/")[-1] + "_entity")
    ow = codecs.open(out_file, "w", encoding="utf8")
    for k in sort_keys:
        datestampe = k[:13]
        word = normalize_str(k[14:].encode("utf8"))
        count = entities[k]
        ow.write("%s\t%s\t%s\n" % (datestampe, word, count))

    ow.flush()
    ow.close()
    print "Finish %s" % tweet_file


def handle_country(in_dir, out_dir):
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    files = os.listdir(in_dir)
    for f in files:
        full_f = os.path.join(in_dir, f)
        extract_entity(full_f, out_dir)


def main():
    in_dir = sys.argv[1]
    out_dir = sys.argv[2]

    handle_country(in_dir, out_dir)


if __name__ == "__main__":
    main()
