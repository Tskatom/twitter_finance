#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import map_reduce
import json

mr = map_reduce.MapReduce(verbose_level=2)


class GetWordCount(object):
    @staticmethod
    def mapper(tweet_file):
        for l in open(tweet_file):
            tweet = json.loads(l)
            for t in tweet['BasisEnrichment']['tokens']:
                mr.emit_intermediate(t['lemma'], 1)

    @staticmethod
    def reducer(key, values):
        mr.emit((key, sum(values)))

if __name__ == "__main__":
    input_files = [sys.argv[1]]
    for key, value in mr.execute(input_files, GetWordCount.mapper, GetWordCount.reducer):
        print key, value

