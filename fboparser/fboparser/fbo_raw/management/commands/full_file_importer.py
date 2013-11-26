from lxml import etree
import re
from datetime import datetime
from fbo_raw.models import Solicitation, Award, Justification, FairOpportunity, ITB, JUSTIFICATION_CHOICES

TOP_LEVEL_TAGS = [
    'PRESOL',
    'COMBINE',
    'AMDCSS',
#    'MOD',
    'AWARD',
    'JA',
    'ITB',
    'FAIROPP',
    'SRCSGT',
    'FSTD',
    'SNOTE',
    'SSALE',
#    'EPSUPLOAD',
#    'DELETE',
#    'ARCHIVE',
#    'UNARCHIVE'
]

def parse_date(date):
    try:
        return datetime.strptime(date, "%m%d%Y")
    except ValueError:
        print("couldn't parse date string %s" % date)
        return None

def parse_money(money_text):
    if money_text:
        money_text = money_text.replace('$', '').replace(',', '')
        money = re.findall('(\d+[.\d]*)', money_text)
        for (i, m) in enumerate(money):
            m = re.sub('[.]\d{2}$', '', m)
            m = m.replace('.', '')
            money[i] = m
        if len(money) > 1:
            print(money_text)
            print("Money string has multiple amounts in it: %s " % money)
            return (0, money_text)

        if len(money) > 0:
            return (money[0], money_text)
        else:
            return (0, money_text)

    else:
        return (0, money_text)

def get_choice(text):
    for tup in JUSTIFICATION_CHOICES:
        if tup[1].lower() == text.lower():
            return tup[0]


def process_notice(elem):
    if elem.tag == 'AWARD':
        a = Award()
    elif elem.tag == 'JA':
        a = Justification()
    elif elem.tag == 'FAIROPP':
        a = FairOpportunity()
    elif elem.tag in ['PRESOL', 'COMBINE', 'SRCSGT', 'SSALE', 'SNOTE', 'FSTD']:
        a = Solicitation()
        a.solicitation_type = elem.tag
    elif elem.tag == 'ITB':
        a = ITB()

    for c in elem.iterchildren():
        if c.tag == 'AWDNBR': a.award_number = c.text
        elif c.tag == 'AWDAMT': a.award_amount, a.award_amount_text = parse_money(c.text)
        elif c.tag == 'AWARDEE': a.awardee = c.text
        elif c.tag == 'AWDDATE': a.award_date = parse_date(c.text)
        elif c.tag == 'CLASSCOD': a.class_code = c.text
        elif c.tag == 'SUBJECT': a.subject = c.text
        elif c.tag == 'NAICS': a.naics = c.text
        elif c.tag == 'DESCRIPTION': a.description = c.text
        elif c.tag == 'LINK': a.link = c.text
        elif c.tag == 'EMAIL': a.email = c.text
        elif c.tag == 'OFFADD': a.office_address = c.text
        elif c.tag == 'ARCHDATE': a.archive_date = parse_date(c.text)
        elif c.tag == 'CORRECTION': a.correction = c.text
        elif c.tag == 'SOLNBR': a.sol_nbr = c.text
        elif c.tag == 'LINENBR': a.line_number = c.text
        elif c.tag == 'STAUTH': a.statutory_authority = c.text # JA only
        elif c.tag == 'MODNBR': a.modification_number = c.text # JA/FAIROPP only 
        elif c.tag == 'DONBR': a.order_number = c.text # FAIROPP only
        elif c.tag == 'FOJA': a.foja = get_choice(c.text) #FAIROPP only
        elif c.tag == 'NTYPE': a.n_type = c.text # ITB only

        #mostly solicitation attributes
        elif c.tag == 'RESPDATE': a.response_date = parse_date(c.text)
        elif c.tag == 'POPADDRESS': a.pop_address = c.text
        elif c.tag == 'POPZIP': a.pop_zip = c.text
        elif c.tag == 'POPCOUNTRY': a.pop_country = c.text
        elif c.tag == 'DATE': a.date = parse_date(c.text)
        elif c.tag == 'SETASIDE': a.setaside = c.text

    a.save()


root = etree.iterparse('FBOFullXML.xml')
counts = {}


for event, elem in root:
    if elem.tag in TOP_LEVEL_TAGS and event=='end':
        process_notice(elem)
        #keep count of notice numbers
        if elem.tag in counts:
            counts[elem.tag] += 1
        else:
            counts[elem.tag] = 1
   
   
#    elem.clear()


print(counts)
           


