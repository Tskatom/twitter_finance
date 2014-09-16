#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import map_reduce
import json
import redis
import os

mr = map_reduce.MapReduce(verbose_level=2)


class GetHourWordCount(object):
    @staticmethod
    def mapper(tweet_file):
        for l in open(tweet_file):
            tweet = json.loads(l)
            #get tweet time stamp
            date_stamp = tweet["date"][:13]
            for t in tweet["BasisEnrichment"]["entities"]:
                mr.emit_intermediate(date_stamp, t["expr"].strip().lower())

    @staticmethod
    def reducer(key, values):
        count = zip(values, map(values.count, values))
        mr.emit((key, count))


def main():
    r = redis.Redis()
    dir = sys.argv[1]
    country = dir.split("/")[-1]
    files = os.listdir(dir)
    input_files = [os.path.join(dir, f) for f in files]

    for key, value in mr.execute(input_files, GetHourWordCount.mapper, GetHourWordCount.reducer):
        print key
        r.set("%s_%s" % (country, key), value)
    r.save()

if __name__ == "__main__":
    main()
