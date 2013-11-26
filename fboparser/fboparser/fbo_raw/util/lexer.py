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

class Token(list):
    def __init__(self, text, sequence_number, begin, end, begin_line, end_line):
        self.text = text
        self.sequence_number = sequence_number
        self.begin_offset = begin
        self.end_offset = end
        self.begin_line = begin_line
        self.end_line = end_line

class Text(Token):
    def __str__(self):
        return 'Text[{b}:{e}]:{t!r}'.format(b=self.begin_offset,
                                            e=self.end_offset,
                                            t=self.text)

    def __repr__(self):
        return '<{0}>'.format(str(self))

class Tag(Token):
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
        return 'Tag[{b}:{e}]:{t} ({n} children)'.format(b=self.begin_offset,
                                                        e=self.end_offset,
                                                        t=self.name,
                                                        n=len(self))

    def __repr__(self):
        return '<{0}>'.format(str(self))

def counter(start):
    value = start
    def _counter():
        nonlocal value
        saved = value
        value += 1
        return saved
    return _counter

def form_tags(chars):
    LINE_ENDINGS = ('\r', '\n')
    window = deque()
    token_sequence_number = counter(0)
    begin_line = 1
    end_line = 1

    # Using start=1 because begining offsets are calculated via subtraction
    # and we want an inclusive ending offset.
    for (offset, chr) in enumerate(chars, start=1):
        window.append(chr)
        # We only count line feeds or carriage returns as line breaks
        # if they are preceded by either an identical characters or
        # a character other than line feed or carriage return.
        if (chr in LINE_ENDINGS
            and (len(window) == 1
                 or window[-2] not in LINE_ENDINGS
                 or window[-2] == chr)):
            end_line += 1
        elif chr == '>':
            window_chars = "".join(window)
            for tag in ALL_TAGS:
                if window_chars.endswith(tag):
                    if len(window_chars) > len(tag):
                        prefix_text = window_chars[:-len(tag)]
                        yield Text(prefix_text,
                                   token_sequence_number(),
                                   offset - len(window_chars),
                                   offset - len(tag),
                                   begin_line,
                                   end_line)
                    tag_text = window_chars[-len(tag):]
                    # A tag has no line endings in it, so the begin and end
                    # lines will always be the same.
                    yield Tag(tag_text,
                              token_sequence_number(),
                              offset - len(tag_text),
                              offset,
                              end_line,
                              end_line)
                    window = deque()
                    begin_line = end_line

    if len(window) > 0:
        remaining_text = "".join(window)
        yield Text(remaining_text,
                   token_sequence_number(),
                   offset - len(remaining_text),
                   offset,
                   begin_line,
                   end_line)

def lex_stream(fobj):
    return form_tags(generate_characters(fobj))

def lex_file(path):
    return lex_stream(open(path, 'r', encoding='utf-8'))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as fobj:
            pprint(list(form_tags(generate_characters(fobj))))
