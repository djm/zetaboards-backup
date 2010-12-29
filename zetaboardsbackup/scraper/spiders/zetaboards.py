from scrapy.conf import settings
from scrapy.exceptions import NotConfigured
from scrapy.http import FormRequest
from scrapy.spider import BaseSpider

from scraper.items import ForumItem, ThreadItem, PostItem, UserItem, UserGroupItem
from scraper.loader import ForumLoader, ThreadLoader, PostLoader, UserLoader, \
        UserGroupLoader

from forum.models import Forum, Thread, Post, User, UserGroup

try:
    USERNAME = settings.ZETABOARDS_USERNAME
except AttributeError:
    raise NotConfigured, "The Scrapy config requires `ZETABOARDS_USERNAME`."
try:
    PASSWORD = settings.ZETABOARDS_PASSWORD
except AttributeError:
    raise NotConfigured, "The Scrapy config requires `ZETABOARDS_PASSWORD`."
try:
    BOARD_URL = settings.ZETABOARDS_BOARD_URL
except AttributeError:
    raise NotConfigured, "`ZETABOARDS_BOARD_URL is not set. Set it to your boards" \
            "full URL WITHOUT the trailing slash."

LOGIN_PATH = getattr(settings, 'ZETABOARDS_LOGIN_PATH', '/login/')


class ZetaboardsSpider(BaseSpider):
    name = 'zetaboards'
    start_urls = "%s%s" % (BOARD_URL, LOGIN_PATH)

    def parse(self, response):
        pass

SPIDER = ZetaboardsSpider()
