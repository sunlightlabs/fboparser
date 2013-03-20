from __future__ import print_function
import sys
from BeautifulSoup import BeautifulSoup as BS

#tags that appear inside the top level tags and aren't closed
broken_tags=['date', 'year', 'agency', 'zip','classcod','naics','offadd','subject','solnbr','respdate','archdate','contact','desc','link','email','links','files','setaside','popaddress','popzip','popcountry','recovery_act','ntype','awdnbr','awddate','awdamt','awardee','awardee_duns','modnbr','donbr','foja', 'office', 'location', 'stauth', 'url']

#these are top level tags, each will have own table
top_level_tags = ['presol', 'combine', 'award', 'ja', 'fairopp', 'mod', 'archive', 'unarchive']

#have beautifulsoup fix unclosed tags inside main nodes

def parse_file(path):
    with file(path, 'rb') as f:
        return parse_stream(f)

def parse_stream(fobj):
    for bt in broken_tags:
        BS.RESET_NESTING_TAGS[bt] = top_level_tags
        BS.NESTABLE_TAGS[bt] = top_level_tags
    soup = BS(fobj)
    return soup

if __name__ == "__main__":
    if len(sys.argv) > 1:
        feed = parse_file(sys.argv[1])
        print(feed.prettify())
