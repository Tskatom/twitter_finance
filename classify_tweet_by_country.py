#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import codecs
import re
import json
import os
from etool import args


RULES = {"Costa Rica": ["costa rica", "costa rican", "costarica"],
         "Brazil": ["brasil", "Brazilian real", "brazil"],
         "Mexico": ["México", "Mexican peso", "mexico"],
         "Panama": ["Panamá", "panama"],
         "Colombia": ["colombia", "Colombian peso"],
         "Argentina": ["argentina", "Argentine peso"],
         "Peru": ["perú", "Peruvian nuevo sol", "peru"],
         "Chile": ["chile", "Chilean peso"],
         "Venezuela": ["venezuela"]}

COUNTRY = ['Costa Rica', 'Brazil', 'Mexico', 'Panama', 'Colombia',
           'Argentina', 'Peru', 'Chile', 'Venezuela']


def filter_by_country(tweet_file, country, source):
    #create regex rule
    pattern = "(" + '|'.join(RULES[country]) + ")"
    #combine the tweet_file by date
    out_dir = "/media/2488-4033/data/filter/" + country.replace(" ", "")
    t_date = re.search(r'\d{4}-\d{2}-\d{2}', tweet_file).group()
    out_file = "%s_%s_%s" % (country.replace(" ", ""), t_date, source)
    out_file = os.path.join(out_dir, out_file)

    country_file = codecs.open(out_file, 'a')

    with codecs.open(tweet_file) as tf:
        for l in tf:
            try:
                tweet = json.loads(l)
            except:
                print "Error: ", l
                continue
            content = tweet['interaction']['content']
            if re.search(pattern, content, flags=re.I):
                tweet["lables"] = [country]
                country_file.write(
                    json.dumps(tweet,
                               ensure_ascii=False).encode('utf8') + '\n')
    country_file.flush()
    country_file.close()


def check_tweets_user(tweet, users):
    #check author
    author_id = tweet['interaction']['author']['id']
    if author_id in users:
        return True

    #check mentions
    if "mentions" in tweet['interaction']:
        mentions = tweet["interaction"]["mention_ids"]
        for _id in mentions:
            if _id in users:
                return True

    #check retweeted
    if "retweeted" in tweet["twitter"]:
        o_id = tweet["twitter"]["retweeted"]\
            .get("user").get("id")
        if o_id in users:
            return True
    return False


def filter_by_userbelong(tweet_file, country):
    country_user_file = "/home/vic/work/twitter_finance/"
    if not os.path.exists(country_user_file):
        country_user_file = '/home/vic/workspace/twitter_finance'
    country_user_file += 'dictionary/country_market_combine_user.txt'

    country_user = json.load(open(country_user_file))
    users = country_user.get(country)
    users = map(int, users)
    #combine tweet_file by date
    out_dir = "/media/datastorage/filter/country/" + country.replace(" ", "")
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    t_date = re.search(r'\d{4}-\d{2}-\d{2}', tweet_file).group()
    out_file = "%s_%s" % (country.replace(" ", ""), t_date)
    out_file = os.path.join(out_dir, out_file)

    with open(tweet_file) as r, open(out_file, "a") as a:
        match_tweets = []
        for l in r:
            tweet = json.loads(l)
            if check_tweets_user(tweet, users):
                match_tweets.append(tweet)
        print tweet_file
        for t in match_tweets:
            a.write(json.dumps(t, ensure_ascii=False).encode('utf-8') + "\n")
        a.flush()


def main():
    ap = args.get_parser()
    ap.add_argument('--folder', type=str, help='the file folder')
    ap.add_argument('--c', dest='country', type=str, nargs='+',
                    help='country list')
    ap.add_argument('--file', type=str, help='tweet file')
    ap.add_argument('--source', type=str, help='data source',
                    default='datasift')
    arg = ap.parse_args()

    if arg.country is not None:
        country_list = arg.country
    else:
        country_list = COUNTRY

    if arg.file:
        for country in country_list:
            filter_by_userbelong(arg.file, country)
    elif arg.folder:
        files = os.listdir(arg.folder)
        for f in files:
            f = os.path.join(arg.folder, f)
            if os.path.isfile(f):
                for country in country_list:
                    filter_by_userbelong(f, country)

if __name__ == "__main__":
    main()
