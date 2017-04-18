import feedparser
from backend.scopes import get_url_for_scope, SCOPE_UPLOADPLAN, SCOPE_NEWS, SCOPE_VIDEO
from email.utils import parsedate
import time


class Feed(object):
    def __init__(self, title, scope, link=None, date=None, desc=None, reddit_url=None):
        self.title = title
        self.link = link
        self.date = date
        self.desc = desc
        self.scope = scope
        self.reddit_url = reddit_url


def parse_feed(scope):
    """
    Get's a feed from the scope url and parses it
    :param scope: For the url and the scope in the object
    :return: a Feed object with all needed data
    """
    d = feedparser.parse(get_url_for_scope(scope))
    new_feeds = []
    for x in range(0, 3):
        try:
            title = d.entries[x].title
            link = d.entries[x].link
            desc = d.entries[x].description
            if (scope == SCOPE_UPLOADPLAN) or (scope == SCOPE_NEWS):
                desc = None
            t = parsedate(d.entries[x].published)
            # Store date as unix milliseconds timestamp so it can be easily parsed in Android
            date = int(time.mktime(t)) * 1000
            
            new_feeds.append(Feed(title=title, link=link, date=date, desc=desc, scope=scope))
        except IndexError:
            print("Index does not exist")
        
        
    return new_feeds

    
