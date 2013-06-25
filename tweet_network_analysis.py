#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import networkx as nx
import re
import json
import os
from etool import args
from collections import Counter
import requests


class Netsis:
    #Activity feature list
    #number of re-tweets in G
    #number of tweets in G
    #number of tweets that mentions users in G
    #number of hashtags used in all tweets in G
    #number of tweets with URLs in G
    #average tweets being sent per user
    #the hotest hashtag
    #the hotest url
    #the hostest retweet

    #Graph feature list
    #number of nodes in G
    #number of edges in G
    #number of connected components in G
    #network density

    def __init__(self, model):
        self.model = model

    def load_graph(self, read_func, graph_file):
        self.g = read_func(graph_file)
        self.nodes = self.g.nodes()
        self.summary = {}
        self.country = self.g.graph["country"]
        self.date = self.g.graph["date"]

    def count_tweet_activity(self):
        self.tweet_mention = []
        self.tweet_hashtag = []
        self.tweet_url = []
        self.retweets = []
        for tweet in self.summary["TWEET"]:
            if tweet in self.g.edge:
                edgs = self.g.edge[tweet]
                for e, attrs in edgs.items():
                    if attrs['type'] == 'MENTION':
                        self.tweet_mention.append(e)
                    elif attrs['type'] == 'ANNOTATED':
                        self.tweet_hashtag.append(e)
                    elif attrs['type'] == 'CITED':
                        self.tweet_url.append(e)
                    elif attrs['type'] == 'RETWEETED':
                        self.retweets.append(tweet)
        self.tweet_num = len(self.summary["TWEET"])
        self.retweet_num = len(self.retweets)
        self.tweet_hashtag_num = len(self.tweet_hashtag)
        self.tweet_url_num = len(self.tweet_url)
        self.tweet_mens_num = len(self.tweet_mention)

    def get_net_density(self):
        self.density = nx.density(self.g)

    def get_num_nodes(self):
        self.num_nodes = self.g.number_of_nodes()

    def get_num_edges(self):
        self.num_edges = self.g.number_of_edges()

    def get_num_weakly(self):
        self.num_weakly_components = nx.weakly_connected\
            .number_weakly_connected_components(self.g)

    def run_summary(self):
        for n in self.nodes:
            node = self.g.node[n]
            type = node['type']
            self.summary.setdefault(type, [])
            self.summary[type].append(n)

        self.count_tweet_activity()

    def get_activity(self):
        self.hot_hashtag_num = max(Counter(self.tweet_hashtag).values())
        #get original urls
        self.o_urls = []
        #for s_url in self.tweet_url:
        #    try:
        #        print s_url
        #        ori_url = requests.get(s_url, timeout=2).url
        #        print "2", ori_url
        #        ori_url = ori_url.split('#')[0]
        #        self.o_urls.append(ori_url)
        #    except:
        #        #add the original url to url list
        #        self.o_urls.append(s_url)
        #        continue
        self.hot_url_num = max(Counter(self.tweet_url).values())

    def analysis(self):
        self.get_net_density()
        self.get_num_nodes()
        self.get_num_edges()
        self.get_num_weakly()
        self.run_summary()
        self.get_activity()

        self.analysis_summary = {
            "tweet_num": self.tweet_num,
            "retweet_num": self.retweet_num,
            "tweet_hash_num": self.tweet_hashtag_num,
            "tweet_url_num": self.tweet_url_num,
            "tweet_mens_num": self.tweet_mens_num,
            "hot_hash_tag": self.hot_hashtag_num,
            "hot_url": self.hot_url_num,
            "node_num": self.num_nodes,
            "edge_num": self.num_edges,
            "weakly_componnet_num": self.num_weakly_components,
            "net_density": self.density,
            "country": self.country,
            "date": self.date}


def analysis_by_file(graph_file, out_folder):
    match = re.search(r'gpickle', graph_file)
    if match is None:
        return

    netsis = Netsis("Tweet_Analysis")
    netsis.load_graph(nx.read_gpickle, graph_file)
    netsis.analysis()
    result = netsis.analysis_summary
    g_date = result["date"]
    target_file = "tweet_finance_analysis_%s" % g_date
    target_file = os.path.join(out_folder, target_file)
    with open(target_file, 'a') as tf:
        tf.write("%s\n" % json.dumps(result, ensure_ascii=False))


def analysis_by_folder(in_folder, out_folder):
    files = os.listdir(in_folder)
    for f in files:
        full_f = os.path.join(in_folder, f)
        if not os.path.isfile(full_f):
            continue
        analysis_by_file(full_f, out_folder)


def main():
    ap = args.get_parser()
    ap.add_argument("--out", type=str,
                    help="the output dir")
    ap.add_argument("--inf", type=str, help="graph files folder")
    ap.add_argument("--files", type=str,
                    nargs='+', help="file list")
    arg = ap.parse_args()
    assert arg.out, "Please Enter a output dir"
    if arg.inf:
        folders = os.listdir(arg.inf)
        for folder in folders:
            full_f = os.path.join(arg.inf, folder)
            if not os.path.isdir(full_f):
                continue
            analysis_by_folder(full_f, arg.out)
    elif arg.files:
        for f in arg.files:
            analysis_by_file(f, arg.out)


if __name__ == "__main__":
    main()
