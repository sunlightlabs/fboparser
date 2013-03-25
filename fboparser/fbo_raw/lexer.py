#!/usr/bin/env python3.3
# encoding: utf-8

from __future__ import print_function

import io
import codecs
import sys
import itertools
from contextlib import closing
from collections import deque
from pprint import pprint


TAG_NAMES = ['ADDRESS', 'AGENCY', 'ALT', 'AMDCSS', 'ARCHDATE', 'ARCHIVE',
             'AWARD', 'AWARDEE', 'AWDAMT', 'AWDDATE', 'AWDNBR', 'BOANBR',
             'CBAC', 'CLASSCOD', 'CMP', 'COMBINE', 'COMBINED',
             'CONTACT', 'CORRECTION', 'CPU', 'CR', 'CSMP', 'DATE', 'DD',
             'DESC', 'DONBR', 'EMAIL', 'EMAILDESC', 'FAIROPP', 'FILE', 'FILELIST',
             'FOJA', 'FSTD', 'GO', 'H', 'HTML', 'IS', 'ITB', 'JA', 'JTR',
             'LINENBR', 'LINK', 'LOCATION', 'MDT', 'MOD', 'MODNBR', 'NAICS',
             'NONE', 'NTYPE', 'OFFADD', 'OFFICE', 'OL', 'P', 'PASSWORD',
             'POPADDRESS', 'POPCOUNTRY', 'POPZIP', 'PRESOL', 'REDACTED',
             'REESPDATE', 'RESERVED', 'RESPDATE', 'SETASIDE', 'SNOTE',
             'SOLNBR', 'SOURCE', 'SRCSGT', 'SSALE', 'STAUTH', 'STRONG',
             'SUBJECT', 'SUP', 'TBD', 'TITLE', 'UNARCHIVE', 'URL', 'YEAR',
             'ZIP']
HTML_TAGS = ['A', 'B', 'BODY', 'BR', 'HEAD', 'I', 'LI', 'P', 'SPAN', 'TBODY',
             'THEAD', 'TR',
             'U', 'UL']


OPEN_TAGS = [ '<{0}>'.format(tag) for tag in TAG_NAMES ]
CLOSE_TAGS = [ '</{0}>'.format(tag) for tag in TAG_NAMES ]
ALL_TAGS = OPEN_TAGS + CLOSE_TAGS

def generate_characters(fobj):
    with closing(fobj) as fobj1:
        while True:
            chr = fobj1.read(1)
            if len(chr) == 0:
                return
            else:
                yield chr

class Tag(list):
    def __init__(self, text):
        self.text = text

    @property
    def closing_tag(self):
        return self.text[1] == '/'

    @property
    def name(self):
        return self.text.strip('</>')

    def __eq__(self, other):
        return isinstance(other, Tag) and self.text == other.text

    def __hash__(self):
        return id(self)

    def __str__(self):
        return 'Tag:{0} ({1} children)'.format(self.name, len(self))

    def __repr__(self):
        return '<{0}>'.format(str(self))

def form_tags(chars):
    window = deque()

    for chr in chars:
        window.append(chr)
        if chr == '>':
            window_chars = "".join(window)
            for tag in ALL_TAGS:
                if window_chars.endswith(tag):
                    if len(window_chars) > len(tag):
                        yield window_chars[:-len(tag)]
                    yield Tag(window_chars[-len(tag):])
                    window = deque()

    if len(window) > 0:
        yield "".join(window)

def lex_stream(fobj):
    return form_tags(generate_characters(fobj))

def lex_file(path):
    return lex_stream(open(path, 'r', encoding='utf-8'))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as fobj:
            pprint(list(form_tags(generate_characters(fobj))))
