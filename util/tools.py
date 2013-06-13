#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
import random
import codecs
import auto_translate as at
import json


def random_sample_users(user_file, out_file, num):
    users = []
    with codecs.open(user_file) as uf:
        for user in uf.readlines():
            user = json.loads(user)
            name = user['screen_name']
            desc = user['description']
            users.append("%s|%s" % (name, desc))
    sampled = random.sample(users, num)

    with codecs.open(out_file, "w") as uw:
        for user in sampled:
            uw.write(user.encode('utf-8') + "\n")

    un = os.environ['NOTIFIER']
    pw = os.environ['NOTIFIER_PWD']
    translator = at.Translator(un, pw)

    translator.get_workspace()
    translator.clear_sheet()
    result = translator.translate_file(out_file, "es", "en")
    return result

if __name__ == "__main__":
    pass
