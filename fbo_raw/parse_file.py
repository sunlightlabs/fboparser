from bs4 import BeautifulSoup
from BeautifulSoup import BeautifulSoup as BS

filename = '/home/kaitlin/envs/fboparser/raw_files/FBOFeed20120412'

f = open(filename).read()

#tags that appear inside the top level tags and aren't closed
broken_tags=['date', 'year', 'agency', 'zip','classcod','naics','offadd','subject','solnbr','respdate','archdate','contact','desc','link','email','links','files','setaside','popaddress','popzip','popcountry','recovery_act','ntype','awdnbr','awddate','awdamt','awardee','awardee_duns','modnbr','donbr','foja', 'office', 'location', 'stauth', 'url']

#these are top level tags, each will have own table
top_level_tags = ['presol', 'combine', 'award', 'ja', 'fairopp', 'mod', 'archive', 'unarchive']

#have beautifulsoup fix unclosed tags inside main nodes
for bt in broken_tags:
    BS.RESET_NESTING_TAGS[bt] = top_level_tags
    BS.NESTABLE_TAGS[bt] = top_level_tags

#parse actual text
soup = BS(f)

#print some stuff
print soup.presol.prettify()
print soup.presol.date.prettify()
print soup.presol.year.prettify()

#g.write(soup.prettify().encode('utf-8'))

