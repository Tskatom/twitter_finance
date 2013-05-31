#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
from twitter_login import login
from twitter_util import makeTwitterRequest
import argparse


def getFriendIds(t, screen_name=None, user_id=None, friends_limit=10000):
    assert screen_name or user_id

    ids = []
    cursor = -1
    while cursor != 0:
        params = dict(cursor=cursor)
        if screen_name is not None:
            params['screen_name'] = screen_name
        else:
            params['user_id'] = user_id

        response = makeTwitterRequest(t, t.friends.ids, **params)

        ids.extend(response['ids'])
        cursor = response['next_cursor']
        print >> sys.stderr,\
            'Fetched %d ids for %s' % (len(ids), screen_name or user_id)
        if len(ids) >= friends_limit:
            break
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', type=str, help='the screen name')
    ap.add_argument('--id', type=str, help='the user id')
    args = ap.parse_args()

    t = login()

    print getFriendIds(t, args.name, args.id)

if __name__ == "__main__":
    main()
