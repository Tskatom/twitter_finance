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
import numpy as np


class Netsis:
    def __init__(self, net_type):
        self.net_type = net_type
        self.net_switch = {"t": self.content_net_analysis,
                           "c": self.comprehend_analysis,
                           "u": self.user_analysis,
                           "e": self.entity_analysis}

    def user_analysis(self):
        """
        number of node, network density, number connected component
        """
        node_number = self.get_node_num("USER")
        total_weight = 0
        for u, v, d in self.g.edges_iter(data=True):
            total_weight += d["weight"]
        average_weight = total_weight / float(len(self.g.edge.keys()))

        #get network density
        self.get_net_density()
        #get connected component
        self.get_num_weakly()
        #average degree
        average_degree = sum(self.g.degree().values()) / float(node_number)
        self.analysis_summary = {
            "country": self.g.graph["country"],
            "date": self.g.graph["date"],
            "node_num": node_number,
            "average_weight": average_weight,
            "density": self.density,
            "average_degree": average_degree,
            "weakly_componnet_num": self.num_weakly_components
        }

    def get_cluster_coefficient(self):
        try:
            self.cluster_coefficient = nx.average_clustering(self.g)
        except:
            self.cluster_coefficient = 0

    def entity_analysis(self):
        """
        number of node, network density, number of connected
        components, cluster coefficient
        """
        entity_num = len(self.g.nodes())
        #get network density
        self.get_net_density()
        #get cluster coefficient
        self.get_cluster_coefficient()

        self.analysis_summary = {
            "country": self.g.graph["country"],
            "date": self.g.graph["date"],
            "entity_num": entity_num,
            "density": self.density,
            "cluster_coefficient": self.cluster_coefficient,
        }

    def content_net_analysis(self):
        self.entity_list = ["IDENTIFIER:URL", "TWITTER:USERNAME",
                            "PERSON", "PRODUCT", "LOCATION",
                            "TWITTER:HASHTAG", "ORGANIZATION",
                            "NATIONALITY"]
        #get number of tweets
        tweet_num = self.get_node_num("TWEET")
        retweet_num = self.get_edge_num("RETWEET")
        mention_num = self.get_edge_num("MENTION")
        #get average volume of top k entities
        for entity in self.entity_list:
            self.top_k_entity_volume(5, entity)
        #get connected component
        conn_component_num = len(nx.connected_components(self.g))
        #get network density
        self.get_net_density()
        #summary
        self.analysis_summary = {
            "country": self.g.graph["country"],
            "date": self.g.graph["date"],
            "tweet_num": tweet_num,
            "retweet_num": retweet_num,
            "mention_num": mention_num,
            "density": self.density,
            "component_num": conn_component_num,
            "top_url": self.entity_vol["IDENTIFIER:URL"],
            "top_person": self.entity_vol["PERSON"],
            "top_product": self.entity_vol["PRODUCT"],
            "top_location": self.entity_vol["LOCATION"],
            "top_hashtag": self.entity_vol["TWITTER:HASHTAG"],
            "top_organization": self.entity_vol["ORGANIZATION"],
            "top_nation": self.entity_vol["NATIONALITY"]}

    def get_node_num(self, node_type):
        count = 0
        for node, d in self.g.nodes_iter(data=True):
            if node_type == d["type"]:
                count += 1
        return count

    def get_edge_num(self, edge_type):
        count = 0
        "TODO: network failed to store type attribute for retweet edge"
        for u, v, d in self.g.edges_iter(data=True):
            if "type" not in d or d["type"] == edge_type:
                count += 1
        return count

    def load_graph(self, read_func, graph_file):
        self.g = read_func(graph_file)
        self.nodes = self.g.nodes()
        self.summary = {}
        self.country = self.g.graph["country"]
        self.date = self.g.graph["date"]
        self.entity_vol = {}

    def top_k_entity_volume(self, k, entity_type):
        count = [0.0]
        for node, d in self.g.nodes_iter(data=True):
            if d["type"] == entity_type:
                count.append(self.g.degree(node))
        count.sort(reverse=True)
        self.entity_vol[entity_type] = np.mean(count[0:k])

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
        if len(self.tweet_hashtag) == 0:
            self.hot_hashtag_num = 0
        else:
            self.hot_hashtag_num = max(Counter(self.tweet_hashtag).values())
        if len(self.tweet_url) == 0:
            self.hot_url_num = 0
        else:
            self.hot_url_num = max(Counter(self.tweet_url).values())

    def analysis(self):
        analysis_func = self.net_switch[self.net_type]
        analysis_func()

    def comprehend_analysis(self):
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


def analysis_by_file(graph_file, out_folder, net_type="t"):
    match = re.search(r'gpickle', graph_file)
    if match is None:
        return
    netsis = Netsis(net_type)
    netsis.load_graph(nx.read_gpickle, graph_file)
    netsis.analysis()
    result = netsis.analysis_summary
    g_date = result["date"]
    target_file = "tweet_finance_analysis_%s" % g_date
    target_file = os.path.join(out_folder, target_file)
    with open(target_file, 'a') as tf:
        tf.write("%s\n" % json.dumps(result, ensure_ascii=False))


def check_filetype(filename, net_type):
    if net_type == "t":
        rule = "content"
    elif net_type == "c":
        rule = "comprehend"
    elif net_type == "u":
        rule = "user2user"
    elif net_type == "e":
        rule = "entity"
    else:
        return False
    match = re.search(rule, filename)
    if match:
        return True
    return False


def analysis_by_folder(in_folder, out_folder, net_type="t"):
    if net_type == "t":
        out_folder = os.path.join(out_folder, "content")
    elif net_type == "c":
        out_folder = os.path.join(out_folder, "comprehend")
    elif net_type == "u":
        out_folder = os.path.join(out_folder, "user2user")
    elif net_type == "e":
        out_folder = os.path.join(out_folder, "entity")

    if not os.path.exists(out_folder):
        os.mkdir(out_folder)

    files = os.listdir(in_folder)
    for f in files:
        full_f = os.path.join(in_folder, f)
        if (not os.path.isfile(full_f)) or (not check_filetype(f, net_type)):
            continue
        analysis_by_file(full_f, out_folder, net_type)


def main():
    ap = args.get_parser()
    ap.add_argument("--out", type=str,
                    help="the output dir")
    ap.add_argument("--inf", type=str, help="graph files folder")
    ap.add_argument("--files", type=str,
                    nargs='+', help="file list")
    ap.add_argument("--net", type=str)
    ap.add_argument("--c_folder", type=str)
    arg = ap.parse_args()
    assert arg.out, "Please Enter a output dir"
    if arg.inf:
        folders = os.listdir(arg.inf)
        for folder in folders:
            full_f = os.path.join(arg.inf, folder)
            if not os.path.isdir(full_f):
                continue
            analysis_by_folder(full_f, arg.out,  arg.net)
    elif arg.files:
        for f in arg.files:
            analysis_by_file(f, arg.out, arg.net)
    elif arg.c_folder:
        analysis_by_folder(arg.c_folder, arg.out, arg.net)


if __name__ == "__main__":
    main()
