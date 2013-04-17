from __future__ import print_function

import sys
import json
import itertools

from pprint import pprint
from collections import deque
from xml.etree import ElementTree as etree

import yaml

from fbo_raw.lexer import Tag, lex_stream

BROKEN_TAGS =  ['DATE', 'YEAR', 'AGENCY', 'ZIP', 'CLASSCOD', 'NAICS',
                'OFFADD', 'SUBJECT', 'SOLNBR', 'RESPDATE', 'ARCHDATE',
                'CONTACT', 'DESC', 'LINK', 'EMAIL', 'LINKS', 'FILES',
                'SETASIDE', 'POPADDRESS', 'POPZIP', 'POPCOUNTRY',
                'RECOVERY_ACT', 'NTYPE', 'AWDNBR', 'AWDDATE', 'AWDAMT',
                'AWARDEE', 'AWARDEE_DUNS', 'MODNBR', 'DONBR', 'FOJA',
                'OFFICE', 'LOCATION', 'STAUTH', 'URL']

TOP_LEVEL_TAGS = [
    'PRESOL',
    'COMBINE',
    'AMDCSS',
    'MOD',
    'AWARD',
    'JA',
    'ITB',
    'FAIROPP',
    'SRCSGT',
    'FSTD',
    'SNOTE',
    'SSALE',
    'EPSUPLOAD',
    'DELETE',
    'ARCHIVE',
    'UNARCHIVE'
]

STRUCTURAL_NESTED_TAGS = {
    'EMAIL': ['ADDRESS', 'DESC'],
    'LINK': ['URL', 'DESC'],
    'DESC': TOP_LEVEL_TAGS
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
    def __init__(self, token, name, text, *args, **kwargs):
        super(Elem, self).__init__(*args, **kwargs)
        self.name = name
        self.text = text
        self.children = []
        self.closes = None
        self.token = token
        self.begin_offset = None
        self.end_offset = None
        self.begin_line = None
        self.end_line = None

    def pprint(self, indent=2, level=0, file=sys.stdout):
        if self.text is None:
            print("{i}{nm}".format(i=" " * (indent *level),
                                   nm=self.name),
                  file=file)
        else:
            print("{i}{nm} => {txt!r}".format(i=" " * (indent * level),
                                            nm=self.name,
                                            txt=self.text),
                  file=file)
        for child in self.children:
            child.pprint(indent=indent, level=level+1, file=file)

    def __str__(self):
        return "<{}>".format(self.name)

    def __repr__(self):
        return "<Elem({})>".format(self.name)

def parse_file(path, encoding):
    elements = generate_elements(lex_stream(open(path, 'r', encoding=encoding)))
    top_level_elems = parse_top_level(elements)
    return top_level_elems

def generate_elements(tokens):
    elem_stack = deque()
    window = deque()

    def _find_opening_elem(closing):
        # TODO: This is broken because a spurious closing tag
        # will clear the stack, even if it occurs inside
        # another element that is paired with a legitimate 
        # closing tag. This can be seen in FBOFeed20090506.
        # The spurious </EMAIL> on 3823 clears the stack,
        # which makes the </PRESOL> on line 3825 match no
        # opening tag.
        nonlocal elem_stack
        while len(elem_stack) > 0:
            candidate = elem_stack.popleft()
            if candidate.name == closing.name:
                return candidate
        return None

    def _elem_from_window():
        nonlocal window, elem_stack
        tag0 = window.popleft()
        txt = "".join([tag.text for tag in window]).strip()
        elem = Elem(tag0, tag0.name, txt if len(txt) > 0 else None)
        elem.begin_offset = tag0.begin_offset
        elem.begin_line = tag0.begin_line
        if len(window) > 0:
            elem.end_offset = window[-1].end_offset
            elem.end_line = window[-1].end_line
        else:
            elem.end_offset = tag0.end_offset
            elem.end_line = tag0.end_line
        elem_stack.appendleft(elem)
        window = deque()
        return elem

    for token in tokens:
        if isinstance(token, Tag):
            if token.closing_tag:
                if len(window) > 0:
                    yield _elem_from_window()
                
                closing_elem = Elem(token, token.name, None)
                closing_elem.closes = _find_opening_elem(closing_elem)
                if closing_elem.closes is not None:
                    # If the tag is a closing tag, but we can't find the
                    # opening tag, it must be a straggler due to invalid
                    # syntax. TODO: Should we log a warning?
                    closing_elem.begin_offset = token.begin_offset
                    closing_elem.end_offset = token.end_offset
                    closing_elem.begin_line = token.begin_line
                    closing_elem.end_line = token.end_line
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
            if len(window) == 0:
                raise Exception("Closing element found but the element window is empty: {0} on line {1}".format(elem, elem.end_line))

            elif elem.closes == window[0]:
                # This is the normal case, where a closing element clears
                # the current window
                head = window.popleft()
                head.children = parse_structure(head, window)
                head.end_offset = elem.end_offset
                window = deque()
                yield head

            else:
                window.append(elem)

        elif isinstance(elem, Elem):
            if len(window) == 0 and elem.name not in TOP_LEVEL_TAGS:
                elem.pprint(file=sys.stderr)
                print("Discarded orphaned non-top-level element: {0} on line {1}".format(elem, elem.begin_line), file=sys.stderr)
            else:
                window.append(elem)

        else:
            raise Exception("Exptecting Elem, got {}".format(elem))

    for elem in window:
        yield elem

def parse_structure(parent, elements):
    ast = []
   
    try:
        while True:
            elem = elements.popleft()

            if elem.closes is not None:
                return ast

            elif parent.name in STRUCTURAL_NESTED_TAGS and elem.name not in STRUCTURAL_NESTED_TAGS[parent.name]:
                elements.appendleft(elem)
                return ast

            elif elem.name in STRUCTURAL_NESTED_TAGS or elem.name in TOP_LEVEL_TAGS:
                elem.children = parse_structure(elem, elements)
                ast.append(elem)

            elif parent.name in STRUCTURAL_NESTED_TAGS and elem.name in STRUCTURAL_NESTED_TAGS[parent.name]:
                ast.append(elem)

            elif parent.name in TOP_LEVEL_TAGS:
                ast.append(elem)

            else:
                elements.appendleft(elem)
                return ast

    except IndexError:
        return ast

    except KeyError:
        import ipdb; ipdb.set_trace()

class ElemEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Elem):
            return {
                'element': o.name,
                'text': o.text,
                'children': o.children,
                'begin': o.begin_offset,
                'end': o.end_offset
            }
        elif isinstance(o, deque):
            return list(o)
        return super(ElemEncoder, self).default(o)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        feed = list(parse_file(sys.argv[1], encoding='iso8859_2'))
        if len(sys.argv) > 2 and sys.argv[-1] == 'ast':
            for elem in feed:
                elem.pprint()
        else:
            json.dump(feed, cls=ElemEncoder, fp=sys.stdout, indent=2)


