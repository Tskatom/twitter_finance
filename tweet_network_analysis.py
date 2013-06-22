#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
import networkx as nx


class Netsis:
    #Activity feature list
    #number of re-tweets in G
    #number of different users that have retweeted in G
    #number of tweets in G
    #number of tweets that mentions users in G
    #number of hashtags used in all tweets in G
    #number of tweets with URLs in G
    #number of different users that post a tweet in G
    #average tweets being sent per user
    #the hotest hashtag
    #the hostes url degree

    #Graph feature list
    #number of nodes in G
    #number of edges in G
    #number of connected components in G
    #in_degree
    #out_degree
    #network density

    def __init__(self, model):
        self.model = model

    def load_graph(self, read_func, graph_file):
        self.g = read_func(graph_file)

    def count_tweets(self):





if __name__ == "__main__":
    pass

