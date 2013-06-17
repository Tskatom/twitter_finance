#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

from twitter_login import login
import twitter_util as tu
import redis
import json
import codecs
import sys


MAX_PAGES = 10
#COUNTRY = ['México', 'Panamá', 'Brasil', 'Colombia',
#           'Perú', 'Venezuela', 'Argentina', 'Chile', 'América Latina']
COUNTRY = ['Chile', 'América Latina', 'Argentina']


def search_tweets(t, r, keywords):
 #   redisId = tu.getRedisIdByScreenName(keywords, 'index')
    redisTweetId = tu.getRedisIdByScreenName(keywords, 'search')
    params = {"q": keywords,
              "count": 100}
 #   if last_since_id:
 #       params["since_id"] = last_since_id
    search_results = tu.makeTwitterRequest(t.search.tweets, **params)
    tweets = search_results['statuses']
    #get the since_id
#    since_id = search_results['search_metadata']['max_id_str']
#    r.set(redisId, since_id)

    for i in range(MAX_PAGES - 1):
        print "page %d" % (i + 1)
        next_results = search_results['search_metadata'].get('next_results')
        if next_results is None:
            break
        kwargs = dict([kv.split('=') for kv in next_results[1:].split('&')])
        max_id = str(long(kwargs['max_id']) - 1)
        kwargs['max_id'] = max_id
        search_results = tu.makeTwitterRequest(t.search.tweets,
                                               **kwargs)
        tweets += search_results['statuses']

        if len(search_results['statuses']) == 0:
            break
        print "Fetched %d tweets so far" % len(tweets)

    for t in tweets:
        r.sadd(redisTweetId, t)
    return tweets


def main():
    t = login()
    r = redis.Redis()
    keywordfile = sys.argv[1]
    outfile = sys.argv[2]
    with codecs.open(keywordfile, 'r') as kf:
        keyword_list = [k.replace("\n", "") for k in kf.readlines()]
    country_words = []
    #construct country combination of the keywords and country
    for country in COUNTRY:
        for word in keyword_list:
            country_words.append("%s %s" % (country, word))

    out_file = codecs.open(outfile, "a")
    for keyword in country_words:
        result = search_tweets(t, r, keyword)
        for res in result:
            out_file.write(
                json.dumps(res,
                           ensure_ascii=False).encode('utf8') + "\n")
        out_file.flush()
    out_file.flush()
    out_file.close()
    r.save()


if __name__ == "__main__":
    main()
