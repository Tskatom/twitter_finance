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


def filter_already_download(friend_ids, r):
    try:
        keys = r.keys()
        new_friend_ids = [_id for _id in friend_ids if tu.getRedisIdByScreenName(_id, 'info.json') not in keys]
        exist_ids = [_id for _id in friend_ids if _id not in new_friend_ids]
    except:
        print "---", friend_ids
    return new_friend_ids, exist_ids


def exploit_network(t, r, start_node, depth_limit=1, friend_limit=200):
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
        #exploit the users only have less than 200 friends
        #
        depth += 1
        (queue, next_queue) = (next_queue, [])
        print "%d level, %d users to be exploited" % (depth, len(queue))
        for screen_name in queue:
            #get friend ids
            friend_ids = getFriends(screen_name=screen_name)
            if len(friend_ids) > friend_limit:
                continue
            filter_friend_ids, exist_friend_ids = filter_already_download(friend_ids, r)
            #get friend Info
            friend_infos = tu.getUserInfo(t, r,
                                          user_ids=filter_friend_ids,
                                          sample=0.2)
            exist_friend_infos = loadUserInfo(exist_friend_ids, r)
            friend_infos.extend(exist_friend_infos)
            next_queue.extend([u['screen_name'] for u in friend_infos])
        users.extend(next_queue)

    return users


def loadUserInfo(friend_ids, r):
    return [eval(r.get(tu.getRedisIdByScreenName(_id, 'info.json'))) for _id in friend_ids]


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
