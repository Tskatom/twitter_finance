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
import re


COUNTRY = ["Argentina", "Brazil", "Chile", "Colombia", "Costa Rica",
           "Peru", "Panama", "Mexico", "Venezuela"]

ENTITIES = ['PRODUCT', 'IDENTIFIER:URL', 'TWITTER:HASHTAG',
            'PERSON', 'IDENTIFIER:MONEY', 'TWITTER:USERNAME',
            'NATIONALITY', 'ORGANIZATION', 'LOCATION']


def comprehend_network(tweet_file):
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
            if "mentions" in tweet['interaction']:
                mentions = tweet['interaction']['mentions']
                for user in mentions:
                    net.add_node(user, type='USER')
                    net.add_edge(tweet_id, user, type='MENTION')
    return net


def update_edge(net, node1, node2, weight=False):
    if not weight:
        net.add_edge(node1, node2)
        return True

    if net.has_edge(node1, node2):
        old_weight = net.get_edge_data(node1, node2).get('weight')
        new_weight = old_weight + 1
    else:
        new_weight = 1

    net.add_weighted_edges_from([(node1, node2, new_weight)])
    return True


def user2user_network(tweet_file):
    net = nx.DiGraph()
    #construct network based on user to user
    #node: user, edge: retweet, mention and reply
    #direction: from information source to destination
    with open(tweet_file, "r") as r:
        for line in r:
            tweet = json.loads(line)
            #extract user information
            user_name = tweet['interaction']['author']['username']
            net.add_node(user_name, type="USER")

            #extract retweet info
            if "retweeted" in tweet['twitter']:
                origin_user = tweet['twitter'].get('retweeted')\
                    .get('user').get('screen_name')
                net.add_node(origin_user, type="USER")
                update_edge(net, origin_user, user_name, True)
            #extract mention info
            if "mentions" in tweet["twitter"]:
                mentions = tweet["twitter"]["mentions"]
                for user in mentions:
                    net.add_node(user, type="USER")
                    update_edge(net, user_name, user, True)
    return net


def get_combination(entities):
    """
    get all the combination of two different entities in a list
    """
    combinations = []
    for i in range(len(entities)):
        for j in range(i + 1, len(entities)):
            combinations.append((entities[i], entities[j]))
    return combinations


def content_based_network(tweet_file):
    """
    construct undirected network based on the relation between tweet and tweet
    Node: tweet, url, hashtag, location, product, person, identifier:money,
    twitter:username, nationality, organization
    edges: retweet(tweet to tweet), mention(tweet to user),
    cited(tweet to other entity)
    """
    net = nx.Graph()
    with open(tweet_file) as tf:
        for line in tf:
            tweet = json.loads(line)
            tweet_id = tweet['twitter']['id']
            tweet_content = tweet['interaction']['content']
            net.add_node(tweet_id, type="TWEET", content=tweet_content)

            entities = tweet["BasisEnrichment"]["entities"]

            for entity in entities:
                neType = entity["neType"]
                value = entity["expr"]
                if neType == "TWITTER:USERNAME":
                    net.add_node(value, type=neType)
                    net.add_edge(tweet_id, value, type="MENTION")
                else:
                    if neType in ENTITIES:
                        net.add_node(value, type=neType)
                        net.add_edge(tweet_id, value, type="CITED")
            #extract retweet info
            if "retweeted" in tweet['twitter']:
                ori_tweet_id = tweet['twitter']["retweeted"]["id"]
                net.add_node(ori_tweet_id, type="TWEET", content=tweet_content)
                net.add_edge(ori_tweet_id, tweet_id, type="RETWEET")
    return net


def entity_network(tweet_file):
    """
    1. construct network based on the entity between entities, if
    two entities occur in the
    same tweets, then create a edge between them.
    2. the weight of edge will add 1 once two entities occur together once
    """
    net = nx.Graph()
    tf = open(tweet_file, "r")
    for line in tf:
        tweet = json.loads(line)
        entities = tweet["BasisEnrichment"]["entities"]
        #lowercase the entity value
        entities = [(e["expr"].strip().lower(), e["neType"]) for e in entities]
        com_entity = get_combination(entities)

        #create node
        for entity in entities:
            net.add_node(entity[0], type=entity[1])
        #create edge pairs
        entity_edge_pairs = []
        for pair in com_entity:
            #get weight of edge:pair format((expr, type), (expr, type))
            u, v = pair[0], pair[1]
            edges = net.edge
            if u[0] not in edges:
                weight = 0
            else:
                weight = edges[u[0]].get(v[0], {"weight": 0}).get("weight", 0)
            weight += 1
            entity_edge_pairs.append((u[0], v[0], weight))
        net.add_weighted_edges_from(entity_edge_pairs)
    tf.close()
    return net


def handle_by_folder(in_dir, out_dir, country, net_func=comprehend_network):
    files = os.listdir(in_dir)
    count = 0
    total = len(files)
    for f in files:
        full_f = os.path.join(in_dir, f)
        if not os.path.isfile(full_f):
            continue
        handle_by_file(out_dir, full_f, country, net_func)
        count += 1
        print "Finish %d / %d" % (count, total)


def handle_by_file(out_dir, tweet_file, country, net_func=comprehend_network):
    try:
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        if net_func == comprehend_network:
            net_type = "comprehend"
        elif net_func == user2user_network:
            net_type = "user2user"
        elif net_func == content_based_network:
            net_type = "content"
        elif net_func == entity_network:
            net_type = "entity"
        else:
            net_type = "normal"

        net = net_func(tweet_file)
        net.graph["country"] = country
        g_date = re.search(r'\d{4}-\d{2}-\d{2}', tweet_file).group()
        net.graph["date"] = g_date
        out_file = os.path.join(out_dir,
                                "graph_%s_%s" % (net_type,
                                                 tweet_file.split(os.sep)[-1]))
        nx.write_gpickle(net, out_file + ".gpickle")
        nx.write_graphml(net, out_file + ".graphml")
    except Exception, e:
        print "Error Encoutered: %s, \n %s" \
            % (tweet_file, sys.exc_info()[0]), e


def main():
    NET_TYPE = {"c": comprehend_network, "u": user2user_network,
                "t": content_based_network, "e": entity_network}
    ap = args.get_parser()
    ap.add_argument('--out', type=str, help='graph output folder',
                    default='./')
    ap.add_argument('--inf', type=str, help='tweet input folder')
    ap.add_argument('--infiles', type=str, nargs='+',
                    help='list of files to be handled')
    ap.add_argument('--c', type=str, nargs='+',
                    help='list of country')
    ap.add_argument('--dirf', type=str,
                    help='The folder directly to he handled')
    ap.add_argument('--net', type=str,
                    help="type of network,each symbol represent each type:c")
    arg = ap.parse_args()

    assert arg.net, "Please input a network type"
    if arg.c and len(arg.c) > 0:
        country_list = arg.c
    else:
        country_list = COUNTRY

    if arg.inf:
        for country in country_list:
            in_folder = os.path.join(arg.inf, country.replace(" ", ""))
            out_folder = os.path.join(arg.out, "graph")
            out_folder = os.path.join(out_folder, country.replace(" ", ""))
            for t in arg.net:
                net_type = NET_TYPE.get(t)
                handle_by_folder(in_folder, out_folder, country, net_type)
    elif arg.infiles:
            for f in arg.infiles:
                for t in arg.net:
                    net_type = NET_TYPE.get(t)
                    handle_by_file(arg.out, f, country_list[0], net_type)
    elif arg.dirf:
        for t in arg.net:
            net_type = NET_TYPE.get(t)
            handle_by_folder(arg.dirf, arg.out, country_list[0], net_type)


if __name__ == "__main__":
    main()
