#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import json
import re
import codecs


def create_rule(rule_file, out_file):
    with codecs.open(rule_file, 'r', encoding='utf8') as r,\
            codecs.open(out_file, 'w', encoding='utf8') as w:
        for line in r.readlines():
            line = json.loads(line)
            rule = {"dist": 6,
                    "ignoreHash": True,
                    "language": 'Spanish'}
            tokens = []
            content = line["content"]
            for t in line['BasisEnrichment']['tokens']:
                t['mode'] = 'any'
                t['neType'] = 'any'
                t['form'] = 'lemma'
                t['value'] = t['value']
                if t['lemma'] is None:
                    t["form"] = 'value'
                tokens.append(t)

            if len(line['BasisEnrichment']['tokens']) == 0:
                words = [wd for wd in re.split(r'[\s\W]', content) if wd]
                for wd in words:
                    t = {}
                    t['mode'] = 'any'
                    t['neType'] = 'any'
                    t['form'] = 'value'
                    t['lemma'] = wd
                    t['value'] = wd
                    tokens.append(t)

            rule[u'tokens'] = tokens
            rule[u'text'] = content
            rule[u'key'] = content
            str = json.dumps(rule, ensure_ascii=False)
            w.write(str + "\n")


def optimize_keytxt(key_file, out_key_file):
    #if lemma is null, then set form as value
    with codecs.open(key_file, "r") as kr, \
            codecs.open(out_key_file, 'w') as kw:
        for line in kr.readlines():
            rule = json.loads(line)
            for token in rule['tokens']:
                if token["lemma"] is None:
                    token["form"] = "value"
            kw.write(json.dumps(rule, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    pass
