#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import codecs
import re
import json
import os
from etool import args


RULES = {"Costa Rica": ["costa rica", "costa rican", "costarica"],
         "Brazil": ["brasil", "Brazilian real", "brazil"],
         "Mexico": ["México", "Mexican peso", "mexico"],
         "Panama": ["Panamá", "panama"],
         "Colombia": ["colombia", "Colombian peso"],
         "Argentina": ["argentina", "Argentine peso"],
         "Peru": ["perú", "Peruvian nuevo sol", "peru"],
         "Chile": ["chile", "Chilean peso"],
         "Venezuela": ["venezuela"]}

COUNTRY = ['Costa Rica', 'Brazil', 'Mexico', 'Panama', 'Colombia',
           'Argentina', 'Peru', 'Chile', 'Venezuela']


def filter_by_country(tweet_file, country, source):
    #create regex rule
    pattern = "(" + '|'.join(RULES[country]) + ")"
    #combine the tweet_file by date
    out_dir = "/media/2488-4033/data/filter/" + country.replace(" ", "")
    t_date = re.search(r'\d{4}-\d{2}-\d{2}', tweet_file).group()
    out_file = "%s_%s_%s" % (country.replace(" ", ""), t_date, source)
    out_file = os.path.join(out_dir, out_file)

    country_file = codecs.open(out_file, 'a')

    with codecs.open(tweet_file) as tf:
        for l in tf:
            try:
                tweet = json.loads(l)
            except:
                print "Error: ", l
                continue
            content = tweet['interaction']['content']
            if re.search(pattern, content, flags=re.I):
                tweet["lables"] = [country]
                country_file.write(
                    json.dumps(tweet,
                               ensure_ascii=False).encode('utf8') + '\n')
    country_file.flush()
    country_file.close()


def main():
    ap = args.get_parser()
    ap.add_argument('--folder', type=str, help='the file folder')
    ap.add_argument('--c', dest='country', type=str, nargs='+',
                    help='country list')
    ap.add_argument('--file', type=str, help='tweet file')
    ap.add_argument('--source', type=str, help='data source',
                    default='datasift')
    arg = ap.parse_args()

    if len(arg.country) > 0:
        country_list = arg.country
    else:
        country_list = COUNTRY

    if arg.file:
        for country in country_list:
            filter_by_country(arg.file, country, arg.source)
    elif arg.folder:
        files = os.listdir(arg.folder)
        for f in files:
            f = os.path.join(arg.folder, f)
            if os.path.isfile(f):
                for country in country_list:
                    filter_by_country(f, country, arg.source)

if __name__ == "__main__":
    main()
