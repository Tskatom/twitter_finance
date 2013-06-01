#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import twitter
from urllib2 import URLError
import time
import json
from random import shuffle


def makeTwitterRequest(t, twitterFunction, max_errors=3, *args, **kwArgs):
    wait_period = 2
    error_count = 0
    while True:
        try:
            return twitterFunction(*args, **kwArgs)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0
            wait_period = handleTwitterHTTPError(e, t, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continue"
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive error encountered"
                raise


def handleTwitterHTTPError(e, t, wait_period=2):
    if wait_period > 3600:  # seconds
        print >> sys.stderr, "Too many retries, Quitting"
        raise e
    if e.e.code == 401:
        print >> sys.stderr, "Encountered 401 Error (Not Authorized)"
        return None
    elif e.e.code in (502, 503):
        print >> sys.stderr, "Encountered %i error, \
                Will retry in %d" % (e.e.code, wait_period)
        time.sleep(wait_period)
        wait_period *= 1.5
        return wait_period
    elif _getRemainingHits(t) == 0:
        status = t.account.rate_limit_status()
        now = time.time()  # UTC
        when_rate_limit_resets = status['reset_time_in_seconds']
        sleep_time = max(when_rate_limit_resets - now, 5)
        print >> sys.stderr, 'Rate limit reached, \
                Retry in %d secs' % sleep_time
        time.sleep(sleep_time)
        return 2
    else:
        print >> sys.stderr, "Unexpected exception: %d" % e.e.code
        time.sleep(wait_period)
        wait_period *= 1.5
        return wait_period


def _getRemainingHits(t):
    return t.account.rate_limit_status()['remaining_hits']


# A template-like function that can get friends or followers
def _getFriendsOrFollowersUsingFunc(func, key_name,
                                    t, r, screen_name=None, user_id=None, limit=10000):
    cursor = -1
    result = []
    while cursor != 0:
        response = makeTwitterRequest(
            t,
            func,
            screen_name=screen_name,
            user_id=user_id,
            cursor=cursor)
        for _id in response['ids']:
            result.append(_id)
            r.sadd(getRedisIdByScreenName(screen_name, key_name), _id)
        cursor = response['next_cursor']
        scard = r.scard(getRedisIdByScreenName(screen_name, key_name))
        print >> sys.stderr, 'Fetched %s ids for %s' % (scard, screen_name)
        if scard >= limit:
            break

    return result


#convenience functions
def getRedisIdByScreenName(screen_name, key_name):
    return '%s$%s' % (screen_name, key_name)


#get userinfo through id
def getUserInfo(
        t,  # twitter connection
        r,  # Redis connection
        screen_names=[],
        user_ids=[],
        verbose=False, sample=1.0):

    if sample < 1.0 and (len(screen_names) >= 300 or len(user_ids) >= 300):
        for lst in [screen_names, user_ids]:
            shuffle(lst)
            lst = lst[:int(len(lst) * sample)]

    info = []
    while len(screen_names) > 0:
        screen_names_str = ','.join(screen_names[:100])
        screen_names = screen_names[100:]

        response = makeTwitterRequest(t, t.users.lookup,
                                      screen_name=screen_names_str)

        if response is None:
            break
        if type(response) is dict:
            response = [response]
        for userinfo in response:
            r.set(getRedisIdByScreenName(userinfo['screen_name'], 'info.json'),
                  json.dumps(userinfo))
            r.set(getRedisIdByScreenName(userinfo['id'], 'info.json'),
                  json.dumps(userinfo))
        info.extend(response)

    while len(user_ids) > 0:
        user_ids_str = ','.join([str(_id) for _id in user_ids[:100]])
        user_ids = user_ids[100:]
        response = makeTwitterRequest(t,
                                      t.users.lookup,
                                      user_id=user_ids_str)
        if response is None:
            break

        if type(response) == dict:
            response = [response]

        for userinfo in response:
            r.set(getRedisIdByScreenName(userinfo['screen_name'], 'info.json'),
                  json.dumps(userinfo))
            r.set(getRedisIdByScreenName(userinfo['id'], 'info.json'),
                  json.dumps(userinfo))
        info.extend(response)

    return info

if __name__ == "__main__":
    pass
