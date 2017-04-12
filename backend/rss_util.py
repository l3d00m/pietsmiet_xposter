import feedparser
from backend.scopes import get_url_for_scope, SCOPE_UPLOADPLAN, SCOPE_NEWS, SCOPE_VIDEO
from backend.scrape_util import scrape_site


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
    try:
        title = d.entries[0].title
        link = d.entries[0].link
        desc = d.entries[0].description
        date = d.entries[0].published
    except IndexError:
        return None;

    if (scope == SCOPE_UPLOADPLAN) or (scope == SCOPE_NEWS):
        desc = scrape_site(link)

    return Feed(title=title, link=link, date=date, desc=desc, scope=scope)
