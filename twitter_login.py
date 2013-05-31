#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
import twitter
from twitter.oauth import write_token_file, read_token_file
from twitter.oauth_dance import oauth_dance


def login():
    #loging to twitter application
    APP_NAME = "Finance_Harvest"
    CONSUMER_KEY = "Bkvk7JFZmzaVpLjGAWBtxQ"
    CONSUMER_SECRET = "y9tugnYJeU8aMNW44o6hwWHC3QVktCYtW3RDm3Mdk"
    TOKEN_FILE = 'out/twitter.oauth'

    try:
        (oauth_token, oauth_token_secret) = read_token_file(TOKEN_FILE)
    except IOError, e:
        print e.errno, e.strerror
        (oauth_token, oauth_token_secret) = oauth_dance(
            APP_NAME, CONSUMER_KEY, CONSUMER_SECRET)

        if not os.path.isdir('out'):
            os.mkdir('out')
        write_token_file(TOKEN_FILE, oauth_token, oauth_token_secret)

    return twitter.Twitter(domain='api.twitter.com', api_version='1.1',
                           auth=twitter.oauth.OAuth(
                               oauth_token, oauth_token_secret,
                               CONSUMER_KEY, CONSUMER_SECRET))


if __name__ == "__main__":
    login()
