#!/usr/bin/env python3.3
# encoding: utf-8

import sys

from collections import Counter

from fbo_raw.parser import parse_file

def print_notice_freq(notices, file=sys.stdout):
    notice_ctr = Counter()
    for notice in notices:
        notice_ctr.update([notice.name])

    for (notice_name, freq) in notice_ctr.most_common():
        print("{nm!s: <9} {freq!s: >7}".format(nm=notice_name,
                                                freq=freq))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        notices = parse_file(sys.argv[1], encoding='iso8859_2')
        print_notice_freq(notices)

