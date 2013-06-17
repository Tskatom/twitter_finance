#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

from etool import args
import sys
import json
import codecs


class Filter:
    def __init__(self, user_file):
        with codecs.open(user_file) as uf:
            self.users = [json.loads(l)['id'] for l in uf]

    def filter(self, tweet):
        try:
            tweet = json.loads(tweet)
        except:
            return False

        #check autorinfo
        author_id = tweet['interaction']['author']['id']
        if author_id in self.users:
            return True
        #check mentions
        if "mention_ids" in tweet["interaction"]:
            for _id in tweet["interaction"]['mention_ids']:
                if _id in self.users:
                    return True

        #check retweeted info
        if "retweeted" in tweet["twitter"]:
            if "user" in tweet["twitter"]["retweeted"]:
                ori_user = tweet["twitter"]["retweeted"]["user"]
                return ori_user["id"] in self.users

        return False


def parse_arg():
    ap = args.get_parser()
    ap.add_argument('--cat', action="store_true",
                    help="Flag: input from stdin")
    ap.add_argument('--user', dest='user_file',
                    type=str, help='User file')
    arg = ap.parse_args()
    return arg


def main():
    arg = parse_arg()
    tweetFilter = Filter(arg.user_file)
    if arg.cat:
        #input from stdin
        ins = codecs.getreader('utf-8')(sys.stdin)
        outs = codecs.getwriter('utf-8')(sys.stdout)
        for t in ins:
            if tweetFilter.filter(t):
                outs.write(t)


if __name__ == "__main__":
    main()
