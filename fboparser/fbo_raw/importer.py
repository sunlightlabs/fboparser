#!/usr/bin/env python3.3
# encoding: utf-8
"""
This module walks the tree of parsed elements, ensures their structure is valid,
and translates them to database models.

The EPSUPLOAD and DELETE notice elements, along with the FILELIST and FILE
attribute tags are ignored because they don't seem to be used.
"""

import sys
import datetime 
import re

from fbo_raw.noticefreq import print_notice_freq
from fbo_raw.parser import parse_file
from fbo_raw.models import Solicitation, Award, Justification, FairOpportunity, ITB

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

def value_zero_or_one(notice, name):
    x = zero_or_one(notice, name)
    if x:
        return x.text
    else:
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
    solnbr = errors.check(one_and_only_one, 'SOLNBR')

    return errors

def validate_award_notice(award):
    errors = ErrorCollector(subject=award)

    awdnbr = errors.check(one_and_only_one, 'AWDNBR')
    awdamt = errors.check(one_and_only_one, 'AWDAMT')
    awardee = errors.check(one_and_only_one, 'AWARDEE')
    awddate = errors.check(one_and_only_one, 'AWDDATE')

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
 
def parse_money(notice, name):
    money_text = zero_or_one(notice, name)
    if money_text:
        money_text = money_text.text.replace('$', '').replace(',', '')
        print(money_text)
        money = re.findall('(\d+[\.*\d]*)', money_text)
        for (i, m) in enumerate(money):
            m = re.sub('[.]\d{2}$', '', m)
            m = m.replace('.', '')
            money[i] = m
        print(money)
        return money
    else:
        return 0

def create_date(notice, name):
    try:
        year = int('20' + one_and_only_one(notice, 'YEAR').text)
        date = zero_or_one(notice, name).text
        if len(date) == 4:
            dateobj = datetime.date(year, int(date[:2]), int(date[2:]))
        elif len(date) == 8:
            dateobj = datetime.date(int(date[4:]), int(date[:2]), int(date[2:4]))
        else:
            dateobj = datetime.date(int('20' + date[4:]), int(date[:2]), int(date[2:4]))
        return dateobj
    except AttributeError:
        return None

def import_file(path, encoding):
    text = ""
    with open(path, 'r', encoding=encoding) as fil:
        text = fil.read()
    feed = parse_file(path, encoding)
    validated = []
    splits = []
    for notice in feed:
        try:
            errors = None

            if notice.name == 'PRESOL' or notice.name == 'COMBINE' or notice.name == 'SRCSGT' or notice.name == 'SSALE' or notice.name == 'SNOTE' or notice.name == 'FSTD':
                errors = validate_presol_notice(notice)
                if errors.none:
                    sol_nbr = one_and_only_one(notice, 'SOLNBR').text
                    sol_type = notice.name
                    s, created = Solicitation.objects.get_or_create(sol_number=sol_nbr, solicitation_type=sol_type)
                    
                    #non required parts
                    s.date = create_date(notice, 'DATE')
                    s.naics = value_zero_or_one(notice, 'NAICS')
                    s.description = value_zero_or_one(notice, 'DESCRIPTION')
                    s.class_code = value_zero_or_one(notice, 'CLASSCOD')
                    s.subject = value_zero_or_one(notice, 'SUBJECT')
                    s.zip_code = value_zero_or_one(notice, 'ZIP')
                    s.setaside = value_zero_or_one(notice, 'SETASIDE')
                    s.contact = value_zero_or_one(notice, 'CONTACT')
                    s.link = value_zero_or_one(notice, 'LINK')
                    s.email = value_zero_or_one(notice, 'EMAIL')
                    s.office_address = value_zero_or_one(notice, 'OFFADD')
                    s.archive_date = create_date(notice, 'ARCHDATE')
                    s.correction = value_zero_or_one(notice, 'CORRECTION')
                    s.response_date = create_date(notice, 'RESPDATE')
                    s.pop_address = value_zero_or_one(notice, 'POPADDRESS')
                    s.pop_zip = value_zero_or_one(notice, 'POPZIP')
                    s.pop_country = value_zero_or_one(notice, 'POPCOUNTRY')
               #     s.recovery_act = zero_or_one(notice, 'SETASIDE')
                    s.save()
                    validated.append(s)

            elif notice.name == 'AWARD':
                errors = validate_award_notice(notice)
                if errors.none:
                    awd_nbr = one_and_only_one(notice, 'AWDNBR').text
                    print(awd_nbr)
                    awd_amt = parse_money(notice, 'AWDAMT')
                    if len(awd_amt) > 1 or len(awd_amt) == 0:
                        #potential split award
                        splits.append(awd_nbr)
                        continue
                    else:
                        awd_amt = awd_amt[0]

                    awardee = one_and_only_one(notice, 'AWARDEE').text
                    awd_date = create_date(notice, 'AWDDATE')
                    award, created = Award.objects.get_or_create(award_number=awd_nbr.replace('-', ''), award_amount=awd_amt, award_date=awd_date, awardee=awardee)

                    award.class_code = value_zero_or_one(notice, 'CLASSCOD')
                    award.naics = value_zero_or_one(notice, 'NAICS')
                    award.subject = value_zero_or_one(notice, 'SUBJECT')
                    award.description = value_zero_or_one(notice, 'DESCRIPTION')
                    award.link = value_zero_or_one(notice, 'LINK')
                    award.email = value_zero_or_one(notice, 'EMAIL')
                    award.office_address = value_zero_or_one(notice, 'OFFADD')
                    award.archive_date = create_date(notice, 'ARCHDATE')
                    award.correction = value_zero_or_one(notice, 'CORRECTION')
                    award.sol_number = value_zero_or_one(notice, 'SOLNBR')
                    award.line_number = value_zero_or_one(notice, 'LINENBR')
                    award.contact = one_and_only_one(notice, 'CONTACT').text
                    award.save() 
                    validated.append(award)
                else:
                    print("Could not import award")
            elif notice.name == 'JA':
                errors = validate_award_notice(notice)
                if errors.none:
                    j_nbr = one_and_only_one(notice, 'AWDNBR').text
                    print(j_nbr)
                    j_amt = parse_money(notice, 'AWDAMT')
                    if len(j_amt) > 1 or len(j_amt) == 0:
                        splits.append(j_nbr)
                        continue
                    else:
                        j_amt = j_amt[0]

                    awardee = one_and_only_one(notice, 'AWARDEE').text
                    awd_date = create_date(notice, 'AWDDATE')
                    ja, created = Justification.objects.get_or_create(award_number=j_nbr.replace('-', ''), award_amount=j_amt, award_date=awd_date, awardee=awardee)

                    ja.naics = value_zero_or_one(notice, 'NAICS')
                    ja.description = value_zero_or_one(notice, 'DESCRIPTION')
                    ja.subject = value_zero_or_one(notice, 'SUBJECT')
                    ja.link = value_zero_or_one(notice, 'LINK')
                    ja.email = value_zero_or_one(notice, 'EMAIL')
                    ja.office_address = value_zero_or_one(notice, 'OFFADD')
                    ja.archive_date = create_date(notice, 'ARCHDATE')
                    ja.sol_number = value_zero_or_one(notice, 'SOLNBR')
                    ja.correction = value_zero_or_one(notice, 'CORRECTION')
                    ja.statutory_authority = one_and_only_one(notice, 'STAUTH').text
                    ja.modification_number = one_and_only_one(notice, 'MODNBR').text
                    ja.contact = one_and_only_one(notice, 'CONTACT').text
                    ja.save() 

                    validated.append(ja)

#            elif notice.name == 'ITB':
                # TODO: Have not tested validating a ITB against real data yet
#                errors = validate_itb_notice(notice)

#            elif notice.name == 'FAIROPP':
#                errors = validate_fairopp_notice(notice)

#            elif notice.name == 'SRCSGT':
#                errors = validate_srcsgt_notice(notice)

#            elif notice.name == 'FSTD':
#                errors = validate_fstd_notice(notice)

#            elif notice.name == 'SNOTE':
#                errors = validate_snote_notice(notice)

#            elif notice.name == 'SSALE':
#                errors = validate_ssale_notice(notice)

#            elif notice.name == 'ARCHIVE':
#                errors = validate_archive_notice(notice)

#            elif notice.name == 'UNARCHIVE':
#                errors = validate_unarchive_notice(notice)

#            if errors is None:
#                print("Warning: Unrecognized notice: {}".format(notice.name))
#            elif errors.none:
#                validated.append(notice)
#            else:
#                print("\033[1;31m", file=sys.stderr)
#                errors.pprint()
#                print("\033[0;33m", file=sys.stderr)
#                notice.pprint(file=sys.stderr)
#                print("\033[0;31m", file=sys.stderr)
#                print(text[notice.begin_offset:notice.end_offset], file=sys.stderr)
#                print("\033[0;0m", file=sys.stderr)

        except (NoSuchElement, MultipleElementsFound) as e:
            print("BUG: the importer failed to catch a vaidation error: {}".format(e), file=sys.stderr)

   # print("Frequency of validated notices:")
   # print_notice_freq(validated)
    print("Possible split awards")
    for s in splits:
        print(s) 

if __name__ == "__main__":
    if len(sys.argv) > 1:
        import_file(sys.argv[1], encoding='iso8859_2')
