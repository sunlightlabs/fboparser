from __future__ import print_function

import sys
import json
import itertools

from pprint import pprint
from collections import deque
from xml.etree import ElementTree as etree

import yaml

from lexer import Tag, lex_stream

BROKEN_TAGS =  ['DATE', 'YEAR', 'AGENCY', 'ZIP', 'CLASSCOD', 'NAICS',
                'OFFADD', 'SUBJECT', 'SOLNBR', 'RESPDATE', 'ARCHDATE',
                'CONTACT', 'DESC', 'LINK', 'EMAIL', 'LINKS', 'FILES',
                'SETASIDE', 'POPADDRESS', 'POPZIP', 'POPCOUNTRY',
                'RECOVERY_ACT', 'NTYPE', 'AWDNBR', 'AWDDATE', 'AWDAMT',
                'AWARDEE', 'AWARDEE_DUNS', 'MODNBR', 'DONBR', 'FOJA',
                'OFFICE', 'LOCATION', 'STAUTH', 'URL']

TOP_LEVEL_TAGS = ['PRESOL', 'COMBINE', 'AWARD', 'JA', 'FAIROPP', 'MOD',
                  'ARCHIVE', 'UNARCHIVE', 'AMDCSS']

STRUCTURAL_NESTED_TAGS = {
    'EMAIL': ['ADDRESS', 'DESC'],
    'LINK': ['URL', 'DESC'],
    #'FILELIST': ['FILE'],
    #'FILE': ['URL', 'MIMETYPE', 'DESC']
}

class CharacterFileIterator(object):
    def __init__(self, fobj):
        self.fobj = fobj

    def __iter__(self):
        return self

    def __next__(self):
        chr = self.fobj.read(1)
        if len(chr) == 1:
            return chr
        else:
            raise StopIteration

class PushBackIterator(object):
    def __init__(self, subiter):
        self.subiter = iter(subiter)

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.subiter)

    def pushback(self, obj):
        self.subiter = itertools.chain([obj] if len(obj) == 1 else iter(obj),
                                       self.subiter)

    def peek(self):
        obj = next(self)
        self.pushback(obj)
        return obj

class Elem(object):
    def __init__(self, name, text, *args, **kwargs):
        super(Elem, self).__init__(*args, **kwargs)
        self.name = name
        self.text = text
        self.children = []
        self.closes = None

def parse_file(path, encoding):
    elements = generate_elements(lex_stream(open(path, 'r', encoding=encoding)))
    top_level_elems = parse_top_level(elements)
    return list(top_level_elems)
    feed = []
    for elem in top_level_elems:
        elem.children = parse_second_level(elem.children)
        feed.append(elem)
    return feed

def generate_elements(tokens):
    elem_stack = deque()
    window = deque()

    def _find_opening_elem(closing):
        nonlocal elem_stack
        while len(elem_stack) > 0:
            candidate = elem_stack.popleft()
            if candidate.name == closing.name:
                return candidate
        return None

    def _elem_from_window():
        nonlocal window, elem_stack
        tag0 = window.popleft()
        txt = "".join(window).strip()
        elem = Elem(tag0.name, txt if len(txt) > 0 else None)
        elem_stack.appendleft(elem)
        window = deque()
        return elem

    for token in tokens:
        if isinstance(token, Tag):
            if token.closing_tag:
                if len(window) > 0:
                    yield _elem_from_window()
                
                closing_elem = Elem(token.name, None)
                closing_elem.closes = _find_opening_elem(closing_elem)
                yield closing_elem

            else:
                if len(window) > 0:
                    yield _elem_from_window()
                window.append(token)

        elif len(window) > 0:
            window.append(token)

    if len(window) > 0:
        yield _elem_from_window()

def parse_top_level(elements):
    window = deque()
    for elem in elements:
        closing_top_level = (isinstance(elem, Elem)
                             and elem.closes is not None
                             and elem.name in TOP_LEVEL_TAGS)
        if closing_top_level:
            while len(window) > 0 and elem.name != window[0].name:
                yield window.popleft()
            top_level = window.popleft()
            top_level.children.extend(window)
            window = deque()
            yield top_level

        elif isinstance(elem, Elem):
            window.append(elem)

    for elem in window:
        yield elem

def parse_second_level(elements):
    second_level_elem = None
    reordered = deque()
    for elem in elements:
        if elem.closes is not None:
            if second_level_elem is not None and elem.name == second_level_elem.name:
                second_level_elem = None
        elif elem.name in STRUCTURAL_NESTED_TAGS:
            second_level_elem = elem
            reordered.append(elem)
        elif second_level_elem is not None:
            if elem.name not in STRUCTURAL_NESTED_TAGS[second_level_elem.name]:
                second_level_elem = None
                reordered.append(elem)
            else:
                second_level_elem.children.append(elem)
        else:
            reordered.append(elem)
    return reordered

class ElemEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Elem):
            return {
                'element': o.name,
                'text': o.text,
                'children': o.children
            }
        return super(ElemEncoder, self).default(o)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        feed = list(parse_file(sys.argv[1], encoding='iso8859_2'))
        json.dump(feed, cls=ElemEncoder, fp=sys.stdout, indent=2)

