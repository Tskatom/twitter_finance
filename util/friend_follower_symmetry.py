#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
from twitter_login import login
import twitter_util as tu
import functools
import redis


def summary(screen_name, r):
    t = login()
    #some wrapper around _getFriendsOrFollowersUsingFunc
    #that bind the first two arguments
    getFriendIds = functools.partial(tu._getFriendsOrFollowersUsingFunc,
                                     t.friends.ids,
                                     'friend_ids',
                                     t,
                                     r)
    getFollowerIds = functools.partial(tu._getFriendsOrFollowersUsingFunc,
                                       t.followers.ids,
                                       'follower_ids',
                                       t,
                                       r)

    #get the data
    getFriendIds(screen_name, limit=sys.maxint)
    getFollowerIds(screen_name, limit=sys.maxint)

    #using Redis to compute the numbers
    n_friends = r.scard(tu.getRedisIdByScreenName(screen_name, 'friend_ids'))
    n_followers = r.scard(tu.getRedisIdByScreenName(screen_name,
                                                    'follower_ids'))

    n_friends_diff_followers = r.sdiffstore(
        'temp', [tu.getRedisIdByScreenName(screen_name,
        'friend_ids'),
        tu.getRedisIdByScreenName(screen_name,
        'follower_ids')])
    r.delete('temp')

    n_followers_diff_friends = r.sdiffstore(
        'temp',
        [tu.getRedisIdByScreenName(screen_name,
        'follower_ids'),
        tu.getRedisIdByScreenName(screen_name,
        'friend_ids')])

    r.delete('temp')

    n_friends_inter_followers = r.sinterstore(
        'temp',
        [tu.getRedisIdByScreenName(screen_name,
        'follower_id'),
        tu.getRedisIdByScreenName(screen_name,
        'friend_id')])

    r.delete('temp')

    print '%s is following %s' % (screen_name, n_friends)
    print '%s is being followerd by %s' % \
        (screen_name, n_followers)
    print '%s of %s is not following back' % \
        (n_friends_diff_followers, n_friends)
    print '%s of %s is not following back by %s' % \
        (n_followers_diff_friends, n_followers, screen_name)
    print '%s has %s mutual friends ' % \
        (screen_name, n_friends_inter_followers)


def main():
    r = redis.Redis()
    screen_name = sys.argv[1]

    summary(screen_name, r)

if __name__ == "__main__":
    main()
