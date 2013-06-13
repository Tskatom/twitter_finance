#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import twitter_util as tu
from twitter_login import login
import functools
import argparse
import redis
import sys


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--start_node', type=str, help='Start node to exploit')
    ap.add_argument('--depth', type=int, help='the depth to exploit')
    return ap.parse_args()


def filter_already_download(friend_ids, r):
    try:
        keys = r.keys()
        new_friend_ids = [_id for _id in friend_ids
                          if tu.getRedisIdByScreenName(_id, 'info.json')
                          not in keys]
        exist_ids = [_id for _id in friend_ids if _id not in new_friend_ids]
    except:
        print "---", friend_ids
    return new_friend_ids, exist_ids


def exploit_network(t, r, start_node, depth_limit=1, friend_limit=200):
    users = []
    node_info = tu.getUserInfo(t, r, screen_names=[start_node])
    users.append(node_info[0]['id'])

    getFriends = functools.partial(
        tu._getFriendsOrFollowersUsingFunc, t.friends.ids,
        'friend_ids', t, r)

    friend_ids = getFriends(screen_name=start_node)

    #apply bread-first to get friends' friends
    depth = 1
    next_queue = [u for u in friend_ids]
    users.extend(next_queue)

    while depth < depth_limit:
        #exploit the users only have less than 200 friends
        #
        depth += 1
        (queue, next_queue) = (next_queue, [])
        print "%d level, %d users to be exploited" % (depth, len(queue))
        for _id in queue:
            #get friend ids
            try:
                friend_ids = getFriends(user_id=_id)
                if len(friend_ids) > friend_limit:
                    print "too much friends %d" % len(friend_ids)
                    continue
                next_queue.extend(friend_ids)
            except:
                print >> sys.stderr, "Error encountered for %s" % _id
                break
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
