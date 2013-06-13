#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import json
import codecs


def merge_term(f1, f2, o3, o4):
    with codecs.open(f1, 'r') as r1,\
            codecs.open(f2, 'r') as r2, codecs.open(o3, 'w') as w3,\
            codecs.open(o4, 'w') as w4:
        term = set()
        for t in r1.readlines():
            t = t.strip()
            term.add(t)
        for t in r2.readlines():
            term.add(t.strip())
        for t in term:
            if len(t) > 4:
                #print "str:  ", str
                w3.write(json.dumps({"content": t}, ensure_ascii=False) + "\n")
                w4.write(t + "\n")


if __name__ == "__main__":
    o1 = '../dictionary/eco_fin_terms_object.txt'
    f1 = '../dictionary/economic_terms.txt'
    f2 = '../dictionary/finance_term.txt'
    o2 = '../dictionary/eco_fin_terms.txt'
    merge_term(f1, f2, o1, o2)
