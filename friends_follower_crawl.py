#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
from twitter_login import login
import redis
import functools
from twitter_util import getUserInfo
from twitter_util import _getFriendsOrFollowersUsingFunc

SCREEN_NAME = sys.argv[1]
DEPTH = sys.argv[2]
t = login()
r = redis.Redis()

getFriends = functools.partial(_getFriendsOrFollowersUsingFunc,
                               t.friends.ids,
                               'friend_ids',
                               t,
                               r)

getFollowers = functools.partial(_getFriendsOrFollowersUsingFunc,
                                 t.followers.ids,
                                 'follower_ids',
                                 t,
                                 r)


def crawl(
        screen_names,
        friends_limit=10000,
        followers_limit=10000,
        depth=1,
        friends_sample=.2,
        followers_sample=.1, ):

    getUserInfo(t, r, screen_names=screen_names)
    for screen_name in screen_names:
        friend_ids = getFriends(screen_name, limit=friends_limit)
        follower_ids = getFollowers(screen_name, limit=followers_limit)
        friends_info = getUserInfo(t, r, user_ids=friend_ids,
                                   sample=friends_sample)
        followers_info = getUserInfo(t, r, user_ids=follower_ids,
                                     sample=followers_sample)
        next_queue = [u['screen_name'] for u in friends_info + followers_info]

        d = 1
        while d < depth:
            d += 1
            (queue, next_queue) = (next_queue, [])
            for _screen_name in queue:
                friend_ids = getFriends(_screen_name, limit=friends_limit)
                follower_ids = getFollowers(_screen_name,
                                            limit=followers_limit)
                next_queue.extend(friend_ids + follower_ids)
                getUserInfo(t, r, user_ids=next_queue)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "Please supply at least one screen name and depth"
    else:
        crawl([SCREEN_NAME, DEPTH])
