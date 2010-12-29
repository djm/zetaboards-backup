import datetime
from scrapy.conf import settings
from scrapy.exceptions import NotConfigured
from scrapy.http import FormRequest
from scrapy.spider import BaseSpider

from scraper.items import ForumItem, ThreadItem, PostItem, UserItem, UserGroupItem
from scraper.loader import ForumLoader, ThreadLoader, PostLoader, UserLoader, \
        UserGroupLoader

from forum.models import Forum, Thread, Post, User, UserGroup

USERNAME = settings.get('ZETABOARDS_USERNAME')
if not USERNAME:
    raise NotConfigured, "The Scrapy config requires `ZETABOARDS_USERNAME`."

PASSWORD = settings.get('ZETABOARDS_PASSWORD')
if not PASSWORD:
    raise NotConfigured, "The Scrapy config requires `ZETABOARDS_PASSWORD`."

BOARD_URL = settings.get('ZETABOARDS_BOARD_URL')
if not BOARD_URL:
    raise NotConfigured, "`ZETABOARDS_BOARD_URL is not set. Set it to your boards" \
            "full URL WITHOUT the trailing slash."

LOGIN_PATH = getattr(settings, 'ZETABOARDS_LOGIN_PATH', '/login/')


class ZetaboardsSpider(BaseSpider):
    name = 'zetaboards'
    start_urls = ["%s%s" % (BOARD_URL, LOGIN_PATH)]

    def parse(self, response):
        return [FormRequest.from_response(response,
            formdata={'uname': USERNAME, 
                      'pw': PASSWORD, 
                      'cookie_on': '1',
                      'tm': '',
                      #'tm': datetime.datetime.now().strftime('%a %d %b %Y %H:%M:%S %Z')
                      },
            callback=self.after_login)]

    def after_login(self, response):
        print response.status
        return

SPIDER = ZetaboardsSpider()
