#-*- coding:utf8 -*-
import redis
import re
import json


def check_rule(rule, tweet):
    if re.search(rule, tweet, flags=re.I):
        return True
    else:
        return False


def format_rule(r):
    pattern = r'^\d+\$info\.json'
    keys = filter(lambda x: re.search(pattern, x), r.keys())
    screen_names = [f.split('$')[0] for f in keys]
    rule_str = r'|'.join(screen_names)
    return rule_str, screen_names


def load_tweet(r, tweet_file, out_file):
    rule, ids = format_rule(r)
    ids = json.loads(open('/home/vic/ids.txt').read())
    print ids
    i = 0
    with open(tweet_file, 'r') as r, open(out_file, 'w') as w:
        for line in r.readlines():
            if i % 2000 == 0:
                print 'Index %d' % i
            obj = json.loads(line)
            #extract author id
            a_id = str(obj['interaction']['author']['id'])
            if a_id in ids:
                w.write(line)
                i += 1
                continue
            #extract mention_ids
            flag = False
            m_ids = obj['interaction'].get('mention_ids', [])
            for _id in m_ids:
                if str(_id) in ids:
                    w.write(line)
                    i += 1
                    flag = True
                    break
            if not flag:
                #extract the retweet info
                if 'retweeted' in obj['twitter']:
                    u_id = obj['twitter']['retweeted']['user']['id_str']
                    if u_id in ids:
                        w.write(line)
            i += 1


def main():
    r = redis.Redis()
    tweet_file = '/media/2488-4033/data/datasift-enriched-2013-06-01-06-01-22.txt'
    out_tweet_file = '/media/2488-4033/data/new_filterd_tweet.txt'
    load_tweet(r, tweet_file, out_tweet_file)


if __name__ == '__main__':
    main()
