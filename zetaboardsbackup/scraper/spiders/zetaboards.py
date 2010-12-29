import datetime
from scrapy.conf import settings
from scrapy.exceptions import NotConfigured
from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

from scraper.items import ForumItem, ThreadItem, PostItem, UserItem, UserGroupItem
from scraper.loaders import ForumLoader, ThreadLoader, PostLoader, UserLoader, \
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

# The LOGIN_PATH should be set to the absolute path which accepts
# POST'd login requests. To view it, check the 'action' attribute
# of your login form. It will however most likely be the default..
LOGIN_PATH = getattr(settings, 'ZETABOARDS_LOGIN_PATH', '/login/log_in/')


class ZetaboardsSpider(BaseSpider):
    name = 'zetaboards'

    def start_requests(self):
        return [FormRequest("%s%s" % (BOARD_URL, LOGIN_PATH),
                            formdata={'uname': USERNAME, 
                            'pw': PASSWORD, 
                            # This will make the cookie permanent as
                            # opposed to only lasting for this session.
                            'cookie_on': '1',
                            # This usually passes the time but is filled
                            # out with JavaScript on the live site and 
                            # therefore doesn't actually seem to be required.
                            'tm': '',
                          },
            callback=self.after_login)]

    def after_login(self, response):
        hxs = HtmlXPathSelector(response)
        # Get all root categories on the page, store them and then fire of a 
        # request to go visit their specific subpage so we can get the subcats.
        root_cats = hxs.select('//table[@class="cat_head"]//h2[not(@class)]')
        items_and_reqs = []
        for cat_selector in root_cats:
            # Load root category as a ForumItem (with no parent)
            cat_load = ForumLoader(ForumItem(), cat_selector)
            cat_load.add_xpath('zeta_id', 'a/@href')
            cat_load.add_xpath('title', 'a/text()')
            cat = cat_load.load_item()
            items_and_reqs.append(cat)
            import ipdb; ipdb.set_trace();
            # Send off a request to process the root category subpage.
            # including the parent forum in the meta. 
            req = Request(cat_selector.select('a/@href').extract()[0],
                          meta={'parent': cat['zeta_id']},
                          callback=self.root_category_subpages)
            items_and_reqs.append(req)
        return items_and_reqs

    def root_category_subpages(self, response):
        return None

SPIDER = ZetaboardsSpider()
