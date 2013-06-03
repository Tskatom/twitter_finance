#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import twitter_util as tu
from twitter_login import login
import functools
import argparse
import redis


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start_node', type=str, help='Start node to exploit')
    ap.add_argument('--depth', type=int, help='the depth to exploit')
    return ap.parse_args()


def exploit_network(t, r, start_node, depth_limit=1):
    users = []
    tu.getUserInfo(t, r, screen_names=[start_node])
    users.append(start_node)

    getFriends = functools.partial(
        tu._getFriendsOrFollowersUsingFunc, t.friends.ids,
        'friend_ids', t, r)

    friend_ids = getFriends(screen_name=start_node)
    #get the userinformation of friends
    friend_infos = tu.getUserInfo(t, r, user_ids=friend_ids, sample=0.2)

    #apply bread-first to get friends' friends
    depth = 1
    next_queue = [u['screen_name'] for u in friend_infos]
    users.extend(next_queue)

    while depth < depth_limit:
        depth += 1
        (queue, next_queue) = (next_queue, [])
        for screen_name in queue:
            #get friend ids
            friend_ids = getFriends(screen_name=screen_name)
            #get friend Info
            friend_infos = tu.getUserInfo(t, r,
                                          user_ids=friend_ids, sample=0.2)
            next_queue.extend([u['screen_name'] for u in friend_infos])
        users.extend(next_queue)

    return users


def main():
    t = login()
    r = redis.Redis()
    args = get_args()
    assert args.start_node, 'Input a start node name(screen name)'
    assert args.depth, 'Input a depth to exploit'
    users = exploit_network(t, r, args.start_node, args.depth)
    print "There are %d of users in the network of %s in depth %d" \
        % (len(users), args.start_node, args.depth)
    r.save()

if __name__ == "__main__":
    main()
