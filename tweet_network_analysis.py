#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import networkx as nx
import re
import json
import os
from etool import args


class Netsis:
    #Activity feature list
    #number of re-tweets in G
    #number of tweets in G
    #number of tweets that mentions users in G
    #number of hashtags used in all tweets in G
    #number of tweets with URLs in G
    #number of different users that post a tweet in G
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

    def count_retweet(self):
        self.retweets = []
        for node, edges in self.g.edge.items():
            for target, attrs in edges.items():
                type = attrs.get('type', None)
                if type == 'RETWEETED':
                    self.retweets.append(target)

    def count_tweet_activity(self):
        self.tweet_mention = []
        self.tweet_hashtag = []
        self.tweet_url = []
        self.retweets = []
        for tweet in self.summary["TWEET"]:
            if tweet in self.g.edges():
                edgs = self.g.edge[tweet]
                for e, attrs in edgs.items():
                    if attrs['type'] == 'MENTION':
                        self.tweet_mention.append(e)
                    elif attrs['type'] == 'ANNOTATED':
                        self.tweet_hashtag.append(e)
                    elif attrs['type'] == 'CITED':
                        self.tweet_url.append(e)
                    elif attrs['type'] == 'RETWEETED':
                        self.retweet.append(tweet)

    def get_net_density(self):
        self.density = nx.density(self.g)

    def get_num_nodes(self):
        self.num_nodes = self.g.number_of_nodes()

    def get_num_edges(self):
        self.num_edges = self.g.number_of_edges()

    def get_num_weakly(self):
        self.num_weakly_components = nx.weakly_connected\
            .number_weakly_connected_components(self.g)

    def summary(self):
        for n in self.nodes():
            node = self.g.node[n]
            type = node['type']
            self.summary[type] = self.summary.setdefult(type, []).append(n)

        self.count_tweet_activity()

    def analysis(self):
        self.get_net_density()
        self.get_num_nodes()
        self.get_num_edges()
        self.get_num_weakly()

        self.analysis_summary = {
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
