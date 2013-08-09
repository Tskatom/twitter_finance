#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Wei Wang"
__email__ = "tskatom@vt.edu"

import os
from etool import queue, args


def main():
    ap = args.get_parser()
    ap.add_argument('--dir')
    arg = ap.parse_args()

    assert arg.pub, "Enter a queue to pub"

    file_folder = arg.dir
    files = os.listdir(file_folder)
    w_queue = queue.open(arg.pub, "w", capture=True)

    for f in files:
        full_f = os.path.join(file_folder, f)
        with open(full_f) as af:
            for d_ana in af:
                temp = d_ana.strip().split("|")
                message = {"country": temp[1],
                           "date": temp[0],
                           "z_value": temp[2],
                           "diff_mag": temp[3]}
                w_queue.write(message)
    w_queue.close()


if __name__ == "__main__":
    main()
