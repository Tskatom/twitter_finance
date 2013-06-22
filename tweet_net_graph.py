#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import networkx as nx
import json
from dateutil import parser
import sys
from etool import args
import os


COUNTRY = ["Argentina", "Brazil", "Chile", "Colombia", "Costa Rica",
           "Peru", "Panama", "Mexico", "Venezuela"]


def load_file(tweet_file):
    net = nx.DiGraph()
    with open(tweet_file, 'r') as t_r:
        i = 0
        for line in t_r.readlines():
            i += 1
            tweet = json.loads(line)
            #extract nodes info from tweet
            user_name = tweet['interaction']['author']['username']  # username
            tweet_id = tweet['twitter']['id']  # tweetId
            tweet_content = tweet['interaction']['content']  # tweet content
            create_time = tweet['interaction']['created_at']
            create_time = parser.parse(create_time)\
                .strftime("%Y-%m-%d %H:%M:%S")
            language = tweet['BasisEnrichment']['language']
            if language is None:
                language = 'Spanish'
            net.add_node(tweet_id, content=tweet_content,
                         lan=language, type='TWEET', created_at=create_time)
            net.add_node(user_name, type='USER')
            net.add_edge(user_name, tweet_id, type='CREATED')

            hashtages = []
            urls = []
            #extract hashtage and url
            for entity in tweet['BasisEnrichment']['entities']:
                if entity['neType'] == "TWITTER:HASHTAG":
                    hashtages.append(entity['expr'])
                elif entity['neType'] == "IDENTIFIER:URL":
                    urls.append(entity['expr'])

            for h_tage in hashtages:
                net.add_node(h_tage, type="TWITTER:HASHTAGE")
                net.add_edge(tweet_id, h_tage, type='ANNOTATED')
            for url in urls:
                net.add_node(url, type='IDENTIFIER:URL')
                net.add_edge(tweet_id, url, type='CITED')

            #extract retweet info
            if "retweeted" in tweet['twitter']:
                #get the source tweetid
                origin_tweet_id = tweet['twitter']['retweeted']['id']
                origin_user_name = tweet['twitter'].get('retweeted')\
                    .get('user').get('screen_name')
                origin_create_time = tweet['twitter']\
                    .get('retweeted').get('created_at')
                origin_create_time = parser.parse(origin_create_time)\
                    .strftime("%Y-%m-%d %H:%M:%S")
                net.add_node(origin_tweet_id, content=tweet_content,
                             lan=language,
                             type='TWEET',
                             created_at=origin_create_time)
                net.add_node(origin_user_name, type='USER')
                net.add_edge(origin_tweet_id, tweet_id, type='RETWEETED')
                net.add_edge(origin_user_name, origin_tweet_id, type='CREATED')

            #extract reply information
            if "in_reply_to_status_id" in tweet['twitter']:
                replied_id = tweet['twitter']['in_reply_to_status_id']
                net.add_node(replied_id, type='TWEET')
                net.add_edge(replied_id, tweet_id, type="REPLIED")

            #extract mention info
            if "mentions" in tweet['twitter']:
                mentions = tweet['twitter']['mentions']
                for user in mentions:
                    net.add_node(user, type='USER')
                    net.add_edge(tweet_id, user, type='MENTION')
    return net


def handle_by_folder(in_dir, out_dir):
    files = os.listdir(in_dir)

    for f in files:
        full_f = os.path.join(in_dir, f)
        if not os.path.isfile(full_f):
            continue
        handle_by_file(out_dir, full_f)


def handle_by_file(out_dir, tweet_file):
    try:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        net = load_file(tweet_file)
        out_file = os.path.join(out_dir,
                                "graph_" + tweet_file.split(os.sep)[-1])
        nx.write_gpickle(net, out_file + ".gpickle")
        nx.write_graphml(net, out_file + ".graphml")
    except:
        print "Error Encoutered: %s, \n %s" % (tweet_file, sys.exc_info()[0])


def main():
    ap = args.get_parser()
    ap.add_argument('--out', type=str, help='tweet file folder',
                    default='./')
    ap.add_argument('--inf', type=str, help='graph out put folder')
    ap.add_argument('--infiles', type=str, nargs='+',
                    help='list of files to be handled')
    ap.add_argument('--c', type=str, nargs='+',
                    help='list of files to be handled')
    ap.add_argument('--dirf', type=str,
                    help='The folder directly to he handled')
    arg = ap.parse_args()

    if arg.c and len(arg.c) > 0:
        country_list = arg.c
    else:
        country_list = COUNTRY

    if arg.inf:
        for country in country_list:
            in_folder = os.path.join(arg.inf, country.replace(" ", ""))
            out_folder = os.path.join(arg.out, "graph")
            out_folder = os.path.join(out_folder, country.replace(" ", ""))
            handle_by_folder(in_folder, out_folder)
    elif arg.infiles:
            for f in arg.infiles:
                handle_by_file(arg.out, f)
    elif arg.dirf:
        handle_by_folder(arg.dirf, arg.out)

if __name__ == "__main__":
    main()
