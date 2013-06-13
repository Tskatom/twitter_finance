#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import networkx as nx
import json


def load_file(tweet_file):
    net = nx.DiGraph()

    with open(tweet_file, 'r') as t_r:
        i = 0
        for line in t_r.readlines():
            print "%d iteration" % i
            i += 1
            tweet = json.loads(line)
            #extract nodes info from tweet
            user_name = tweet['interaction']['author']['username']  # username
            tweet_id = tweet['twitter']['id']  # tweetId
            tweet_content = tweet['interaction']['content']  # tweet content
            create_time = tweet['interaction']['created_at']
            language = tweet['BasisEnrichment']['language']

            net.add_node(tweet_id, content=tweet_content,
                         time=create_time, lan=language, type='TWEET')
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
                origin_user_name = tweet['twitter']['retweeted']['user']['screen_name']
                origin_create_time = tweet['twitter']['retweeted']['created_at']
                net.add_node(origin_tweet_id, content=tweet_content,
                             time=origin_create_time, lan=language, type='TWEET')
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


def main():
    tweet_file = '/media/2488-4033/data/filterd_tweet.txt'
    net = load_file(tweet_file)
    nx.write_graphml(net, '/media/2488-4033/data/tweet.graphml')


if __name__ == "__main__":
    main()
