#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import sys
import os
from subprocess import call


def main():
    files_f = sys.argv[1]
    files = [l.strip() for l in open(files_f)]
    for f in files:
        full_f = "/media/datastorage/data/tweets/201305/" + f
        key_py = "python /home/vic/work/scratch/prototype/keyPhraseFinder.py"
        phrase_file = "/home/vic/work/twitter_finance/dictionary/company_key_phrase.txt"
        out_f = "/media/datastorage/filter/company/filter_" + f

        command = "cat %s | %s -m -f %s --cat > %s " % (full_f, key_py, phrase_file, out_f)
        call(command, shell=True)

if __name__ == "__main__":
    main()

