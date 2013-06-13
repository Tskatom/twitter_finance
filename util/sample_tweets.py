#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"


def sample_tweet(tweet_file):
    tweets = []
    with open(tweet_file, 'r') as r:
        tweets = [line for line in r.readlines()]

    import random
    import json
    sample_tweets = random.sample(tweets, 100)
    with open('check_tweets.txt', 'w') as w:
        for t in sample_tweets:
            tweet = json.loads(t)
            w.write("|--| " + tweet['interaction']['content'].encode('UTF-8') + '\n')

if __name__ == "__main__":
    pass
