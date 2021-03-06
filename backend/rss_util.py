import time
from email.utils import parsedate

import feedparser

from backend.scopes import get_url_for_scope, SCOPE_UPLOADPLAN, SCOPE_NEWS, SCOPE_VIDEO
from backend.log_util import log


class Feed(object):
    def __init__(self, title, scope, link=None, date=None, desc=None, reddit_url=None, image_url=None):
        self.title = title
        self.link = link
        self.date = date
        self.desc = desc
        self.scope = scope
        self.reddit_url = reddit_url
        self.image_url = image_url


def find_feed_in_array(feed, feed_list):
    for feed_from_list in feed_list:
        # Compare feed against all feeds from array
        if (feed.title == feed_from_list.title) or (feed.link == feed_from_list.link):
            return feed_from_list
    return False


def parse_feed(scope, limit):
    """
    Get's a feed from the scope url and parses it
    :param limit: How many feeds to return
    :param scope: For the url and the scope in the object
    :return: a Feed object with all needed data
    """
    d = feedparser.parse(get_url_for_scope(scope))
    new_feeds = []
    for x in range(0, limit):
        try:
            title = d.entries[x].title
            image_url = None
            link = d.entries[x].link
            desc = d.entries[x].description
            if (scope == SCOPE_UPLOADPLAN) or (scope == SCOPE_NEWS) or (scope == SCOPE_VIDEO):
                desc = None
            if scope == SCOPE_VIDEO:
                image_url = get_image_url(d.entries[x])

            t = parsedate(d.entries[x].published)
            # Store date as unix milliseconds timestamp so it can be easily parsed in Android
            # Timestamp should be GMT then
            # 1 hour is added to fix the time being wrong because of timezones etc.
            date = int(time.mktime(t) + 3600) * 1000

            new_feeds.append(Feed(title=title, link=link, date=date, desc=desc, scope=scope, image_url=image_url))
        except IndexError:
            pass

    return new_feeds


def get_image_url(entry):
    try:
        for item in entry.media_content:
            item_type = str(item['type'])
            if item_type.startswith("image/"):
                return item['url']
    except Exception:
        pass
    return None
