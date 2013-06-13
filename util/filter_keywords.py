#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import codecs
import json
import random


#COUNTRY = ['Brazil', 'Mexico', 'Costa Rica', 'Colombia',
#           'Panama', 'Venezuela', 'Chile', 'Argentina', 'Peru', 'Brasil']
COUNTRY = ['Costa Rica']


def load_matched(tweet_file):
    count_t = {}
    with codecs.open(tweet_file, 'r') as t_f:
        m_tweets = [json.loads(s) for s in t_f.readlines()]
        for t in m_tweets:
            country = t['embersGeoCode']['country']
            if country is None:
                if "user" in t["twitter"]:
                    country = t["twitter"]["user"].get("location", None)
            if country not in COUNTRY:
                continue
            ps = '|'.join(t['keyPhrases']['phrasesPresent']['phrases'])
            c = count_t.setdefault(ps, 0)
            count_t[ps] = c + 1

    t_count = list(count_t.items())
    return sorted(t_count, key=lambda x: x[1], reverse=True)


def sample_matched(tweet_file, order_key, sampled_file):
    key_tweets = {}
    with codecs.open(tweet_file, 'r') as t_f:
        for t in t_f.readlines():
            t = json.loads(t)
            country = t['embersGeoCode']['country']
            if country is None:
                if "user" in t["twitter"]:
                    country = t["twitter"]["user"].get("location", None)
            if country not in COUNTRY:
                continue
            key = '|'.join(t['keyPhrases']['phrasesPresent']['phrases'])
            content = t['interaction']['content']
            if key not in key_tweets:
                key_tweets[key] = []
            key_tweets[key].append((country, content))
    #for each keys, randomly choose 20% as sample to check
    sample_w = codecs.open(sampled_file, 'w')
    for key in order_key:
        ts = key_tweets[key[0]]
        random.shuffle(ts)
        sample_ts = ts[0: 50]
        #get country info
        for tweet in sample_ts:
            sample_w.write("(%s, %d) | %s\n" %
                           (key[0].encode("utf-8"), key[1],
                            ", ".join(tweet).replace('"', '').encode("utf-8")))


if __name__ == "__main__":
    pass
