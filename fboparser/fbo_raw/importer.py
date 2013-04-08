#!/usr/bin/env python3.3
# encoding: utf-8
"""
This module walks the tree of parsed elements, ensures their structure is valid,
and translates them to database models.

The EPSUPLOAD and DELETE notice elements, along with the FILELIST and FILE
attribute tags are ignored because they don't seem to be used.
"""

import sys

from fbo_raw.noticefreq import print_notice_freq
from fbo_raw.parser import parse_file

class NoSuchElement(Exception):
    def __init__(self, name, *args, **kwargs):
        msg = "Missing {} element".format(name)
        super(NoSuchElement, self).__init__(msg, *args, **kwargs)

class MultipleElementsFound(Exception):
    def __init__(self, name, cnt, *args, **kwargs):
        msg = "Multiple {0} elements found ({1})".format(name, cnt)
        super(MultipleElementsFound, self).__init__(msg, *args, **kwargs)

def one_and_only_one(notice, elname):
    matches = [el for el in notice.children if el.name == elname]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) == 0:
        raise NoSuchElement(elname)
    else:
        raise MultipleElementsFound(elname, len(matches))

def zero_or_one(notice, elname):
    try:
        return one_and_only_one(notice, elname)
    except NoSuchElement:
        return None

class ErrorCollector(object):
    def __init__(self, subject):
        self.subject = subject
        self.errors = []

    @property
    def none(self):
        return len(self.errors) == 0

    def check(self, checkfunc, *args, subject=None, **kwargs):
        try:
            return checkfunc(subject or self.subject, *args, **kwargs)
        except (NoSuchElement, MultipleElementsFound) as e:
            self.errors.append(e)
            return None
   
    def pprint(self, file=sys.stderr):
        print("Failed to validate {sub} from lines {begin}-{end} because:".format(
                  sub=self.subject,
                  begin=self.subject.begin_line,
                  end=self.subject.end_line),
              file=file)
        for error in self.errors:
            print("    {e}".format(e=error), file=file)

    def __iter__(self):
        return iter(self.errors)

    def __add__(self, other):
        result = errors()
        result.errors.extend(self.errors)
        result.errors.extend(other.errors)
        return result

    def __iadd__(self, other):
        self.errors.extend(other.errors)
        return self

def validate_link_and_email(notice):
    errors = ErrorCollector(subject=notice)

    link = errors.check(zero_or_one, 'LINK')
    if link:
        link_url = errors.check(zero_or_one, 'URL', subject=link)
        link_desc = errors.check(zero_or_one, 'DESC', subject=link)


    # Drop empty EMAIL children
    # EMAIL elements are commonly abused in the FBO data
    notice.children = [e for e in notice.children
                       if e.name != 'EMAIL'
                       or len(e.children) > 0]

    email = errors.check(zero_or_one, 'EMAIL')
    if email:
        email_address = errors.check(zero_or_one, 'ADDRESS', subject=email)
        email_desc = errors.check(zero_or_one, 'DESC', subject=email)

    return errors

def validate_presol_notice(presol):
    errors = ErrorCollector(subject=presol)

    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    zip = errors.check(one_and_only_one, 'ZIP')
    classcod = errors.check(one_and_only_one, 'CLASSCOD')
    naics = errors.check(zero_or_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    solnbr = errors.check(one_and_only_one, 'SOLNBR')
    respdate = errors.check(zero_or_one, 'RESPDATE')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    contact = errors.check(one_and_only_one, 'CONTACT')
    desc = errors.check(zero_or_one, 'DESC')
    errors += validate_link_and_email(presol)
    setaside = errors.check(zero_or_one, 'SETASIDE')
    popaddress = errors.check(zero_or_one, 'POPADDRESS')
    popzip = errors.check(zero_or_one, 'POPZIP')
    popcountry = errors.check(zero_or_one, 'POPCOUNTRY')

    return errors

def validate_combine_amdcss_mod_notice(combine):
    errors = ErrorCollector(subject=combine)

    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    zip = errors.check(one_and_only_one, 'ZIP')
    classcod = errors.check(one_and_only_one, 'CLASSCOD')
    naics = errors.check(zero_or_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    solnbr = errors.check(one_and_only_one, 'SOLNBR')
    respdate = errors.check(zero_or_one, 'RESPDATE')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    contact = errors.check(one_and_only_one, 'CONTACT')
    desc = errors.check(zero_or_one, 'DESC')
    errors += validate_link_and_email(combine)
    setaside = errors.check(zero_or_one, 'SETASIDE')
    popaddress = errors.check(zero_or_one, 'POPADDRESS')
    popzip = errors.check(zero_or_one, 'POPZIP')
    popcountry = errors.check(zero_or_one, 'POPCOUNTRY')

    return errors


def validate_award_notice(award):
    errors = ErrorCollector(subject=award)

    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    zip = errors.check(zero_or_one, 'ZIP')
    classcod = errors.check(one_and_only_one, 'CLASSCOD')
    naics = errors.check(zero_or_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    solnbr = errors.check(zero_or_one, 'SOLNBR')
    ntype = errors.check(zero_or_one, 'NTYPE')
    desc = errors.check(zero_or_one, 'DESC')
    contact = errors.check(one_and_only_one, 'CONTACT')
    awdnbr = errors.check(one_and_only_one, 'AWDNBR')
    awdamt = errors.check(one_and_only_one, 'AWDAMT')
    linenbr = errors.check(zero_or_one, 'LINENBR')
    awddate = errors.check(one_and_only_one, 'AWDDATE')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    awardee = errors.check(one_and_only_one, 'AWARDEE')
    awardee_duns = errors.check(zero_or_one, 'AWARDEE_DUNS')
    errors += validate_link_and_email(award)
    setaside = errors.check(zero_or_one, 'SETASIDE')
    correction = errors.check(zero_or_one, 'CORRECTION')

    return errors

def validate_ja_notice(ja):
    errors = ErrorCollector(subject=ja)
    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    zip = errors.check(zero_or_one, 'ZIP')
    classcod = errors.check(one_and_only_one, 'CLASSCOD')
    naics = errors.check(one_and_only_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    ntype = errors.check(zero_or_one, 'NTYPE')
    desc = errors.check(zero_or_one, 'DESC')
    contact = errors.check(one_and_only_one, 'CONTACT')
    stauth = errors.check(one_and_only_one, 'STAUTH')
    awdnbr = errors.check(one_and_only_one, 'AWDNBR')
    modnbr = errors.check(zero_or_one, 'MODNBR')
    awddate = errors.check(one_and_only_one, 'AWDDATE')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    errors += validate_link_and_email(ja)
    correction = errors.check(zero_or_one, 'CORRECTION')
    return errors

def validate_itb_notice(itb):
    errors = ErrorCollector(subject=itb)
    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    zip = errors.check(zero_or_one, 'ZIP')
    classcod = errors.check(one_and_only_one, 'CLASSCOD')
    naics = errors.check(one_and_only_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    solnbr = errors.check(zero_or_one, 'SOLNBR')
    ntype = errors.check(zero_or_one, 'NTYPE')
    desc = errors.check(one_and_only_one, 'DESC')
    contact = errors.check(one_and_only_one, 'CONTACT')
    awdnbr = errors.check(zero_or_one, 'AWDNBR')
    donnbr = errors.check(zero_or_one, 'DONNBR')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    errors += validate_link_and_email(itb)
    correction = errors.check(zero_or_one, 'CORRECTION')
    return errors

def validate_fairopp_notice(fairopp):
    errors = ErrorCollector(subject=fairopp)
    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    zip = errors.check(zero_or_one, 'ZIP')
    classcod = errors.check(one_and_only_one, 'CLASSCOD')
    naics = errors.check(one_and_only_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    solnbr = errors.check(zero_or_one, 'SOLNBR')
    ntype = errors.check(zero_or_one, 'NTYPE')
    desc = errors.check(zero_or_one, 'DESC')
    contact = errors.check(one_and_only_one, 'CONTACT')
    foja = errors.check(one_and_only_one, 'FOJA')
    awdnbr = errors.check(one_and_only_one, 'AWDNBR')
    donnbr = errors.check(one_and_only_one, 'DONNBR')
    modnbr = errors.check(zero_or_one, 'MODNBR')
    awddate = errors.check(one_and_only_one, 'AWDDATE')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    errors += validate_link_and_email(fairopp)
    correction = errors.check(zero_or_one, 'CORRECTION')
    return errors

def validate_srcsgt_notice(srcsgt):
    errors = ErrorCollector(subject=srcsgt)
    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    zip = errors.check(one_and_only_one, 'ZIP')
    classcod = errors.check(one_and_only_one, 'CLASSCOD')
    naics = errors.check(zero_or_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    solnbr = errors.check(one_and_only_one, 'SOLNBR')
    respdate = errors.check(zero_or_one, 'RESPDATE')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    contact = errors.check(one_and_only_one, 'CONTACT')
    desc = errors.check(zero_or_one, 'DESC')
    errors += validate_link_and_email(srcsgt)
    setaside = errors.check(zero_or_one, 'SETASIDE')
    popaddress = errors.check(zero_or_one, 'POPADDRESS')
    popzip = errors.check(zero_or_one, 'POPZIP')
    popcountry = errors.check(zero_or_one, 'POPCOUNTRY')
    return errors

def validate_fstd_notice(fstd):
    errors = ErrorCollector(subject=fstd)
    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    solnbr = errors.check(zero_or_one, 'SOLNBR')
    zip = errors.check(one_and_only_one, 'ZIP')
    classcod = errors.check(zero_or_one, 'CLASSCOD')
    naics = errors.check(zero_or_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    desc = errors.check(zero_or_one, 'DESC')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    contact = errors.check(zero_or_one, 'CONTACT')
    errors += validate_link_and_email(fstd)
    return errors

def validate_snote_notice(snote):
    errors = ErrorCollector(subject=snote)
    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    zip = errors.check(one_and_only_one, 'ZIP')
    solnbr = errors.check(zero_or_one, 'SOLNBR')
    classcod = errors.check(zero_or_one, 'CLASSCOD')
    naics = errors.check(zero_or_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    desc = errors.check(zero_or_one, 'DESC')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    contact = errors.check(zero_or_one, 'CONTACT')
    errors += validate_link_and_email(snote)
    return errors

def validate_ssale_notice(ssale):
    errors = ErrorCollector(subject=ssale)
    date = errors.check(one_and_only_one, 'DATE')
    year = errors.check(one_and_only_one, 'YEAR')
    solnbr = errors.check(zero_or_one, 'SOLNBR')
    zip = errors.check(one_and_only_one, 'ZIP')
    classcod = errors.check(zero_or_one, 'CLASSCOD')
    naics = errors.check(zero_or_one, 'NAICS')
    offadd = errors.check(zero_or_one, 'OFFADD')
    subject = errors.check(one_and_only_one, 'SUBJECT')
    contact = errors.check(one_and_only_one, 'CONTACT')
    desc = errors.check(zero_or_one, 'DESC')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    errors += validate_link_and_email(ssale)
    return errors

def validate_archive_notice(archive):
    errors = ErrorCollector(subject=archive)
    date = errors.check(zero_or_one, 'DATE')
    year = errors.check(zero_or_one, 'YEAR')
    solnbr = errors.check(one_and_only_one, 'SOLNBR')
    ntype = errors.check(zero_or_one, 'NTYPE')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    return errors

def validate_unarchive_notice(unarchive):
    errors = ErrorCollector(subject=unarchive)
    solnbr = errors.check(zero_or_one, 'SOLNBR')
    ntype = errors.check(zero_or_one, 'NTYPE')
    awdnbr = errors.check(zero_or_one, 'AWDNBR')
    archdate = errors.check(zero_or_one, 'ARCHDATE')
    return errors

def import_file(path, encoding):
    text = ""
    with open(path, 'r', encoding=encoding) as fil:
        text = fil.read()
    feed = parse_file(path, encoding)
    validated = []
    for notice in feed:
        try:
            errors = None

            if notice.name == 'PRESOL':
                errors = validate_presol_notice(notice)

            elif notice.name == 'COMBINE':
                errors = validate_combine_amdcss_mod_notice(notice)

            elif notice.name == 'AMDCSS':
                errors = validate_combine_amdcss_mod_notice(notice)

            elif notice.name == 'MOD':
                errors = validate_combine_amdcss_mod_notice(notice)

            elif notice.name == 'AWARD':
                errors = validate_award_notice(notice)

            elif notice.name == 'JA':
                # TODO: Have not tested validating a JA against real data yet
                errors = validate_ja_notice(notice)

            elif notice.name == 'ITB':
                # TODO: Have not tested validating a ITB against real data yet
                errors = validate_itb_notice(notice)

            elif notice.name == 'FAIROPP':
                errors = validate_fairopp_notice(notice)

            elif notice.name == 'SRCSGT':
                errors = validate_srcsgt_notice(notice)

            elif notice.name == 'FSTD':
                errors = validate_fstd_notice(notice)

            elif notice.name == 'SNOTE':
                errors = validate_snote_notice(notice)

            elif notice.name == 'SSALE':
                errors = validate_ssale_notice(notice)

            elif notice.name == 'ARCHIVE':
                errors = validate_archive_notice(notice)

            elif notice.name == 'UNARCHIVE':
                errors = validate_unarchive_notice(notice)

            if errors is None:
                print("Warning: Unrecognized notice: {}".format(notice.name))
            elif errors.none:
                validated.append(notice)
            else:
                print("\033[1;31m", file=sys.stderr)
                errors.pprint()
                print("\033[0;33m", file=sys.stderr)
                notice.pprint(file=sys.stderr)
                print("\033[0;31m", file=sys.stderr)
                print(text[notice.begin_offset:notice.end_offset], file=sys.stderr)
                print("\033[0;0m", file=sys.stderr)

        except (NoSuchElement, MultipleElementsFound) as e:
            print("BUG: the importer failed to catch a vaidation error: {}".format(e), file=sys.stderr)

    print("Frequency of validated notices:")
    print_notice_freq(validated) 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        import_file(sys.argv[1], encoding='iso8859_2')
