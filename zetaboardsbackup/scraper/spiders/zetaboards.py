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
        """
        Crawl the main index to get all root categories.
        """
        hxs = HtmlXPathSelector(response)
        # Get all root categories on the page, store them and then fire of a 
        # request to go visit their specific subpage so we can get the subcats.
        root_cats = hxs.select('//table[@class="cat_head"]//h2[not(@class)]/a')
        items_and_reqs = []
        for cat_selector in root_cats:
            # Load root category as a ForumItem (with no parent)
            cat_load = ForumLoader(ForumItem(), cat_selector)
            cat_load.add_xpath('zeta_id', '@href')
            cat_load.add_xpath('title', 'text()')
            cat = cat_load.load_item()
            items_and_reqs.append(cat)
            # Send off a request to process the root category subpage.
            # including the parent forum in the meta. 
            req = Request(cat_selector.select('@href').extract()[0],
                          meta={'parent': cat['zeta_id']},
                          callback=self.root_category_subpages)
            items_and_reqs.append(req)
        return items_and_reqs

    def root_category_subpages(self, response):
        """
        Crawl the root category pages to get all their sub categories.
        """
        hxs = HtmlXPathSelector(response)
        sub_cats = hxs.select('//tr[@class="forum"]/td[@class="c_forum"]/strong/a')
        items_and_reqs = []
        for cat_selector in sub_cats:
            cat_load = ForumLoader(ForumItem(), cat_selector)
            cat_load.add_xpath('zeta_id', '@href')
            cat_load.add_xpath('title', 'text()')
            cat_load.add_value('parent', response.request.meta['parent'])
            cat = cat_load.load_item()
            items_and_reqs.append(cat)
            # Send off a request to process the root category subpage.
            # including the parent forum in the meta. 
            req = Request(cat_selector.select('@href').extract()[0],
                          meta={'parent': cat['zeta_id']},
                          callback=self.thread_list)
            items_and_reqs.append(req)
        return items_and_reqs

    def thread_list(self, response):
        """
        Crawl the forum index thread list to calculate how many pages need
        to be requested (the pagination range).
        """
        hxs = HtmlXPathSelector(response)
        # We now need to work out how many pages are in this forum.
        last_page = hxs.select('//ul[@class="cat-pages"]/li[last()]/a/text()').extract()[0]
        page_range = range(1, int(last_page)+1)
        reqs = []
        for page in page_range:
            req = Request("%s%i/" % (response.url, page),
                          meta={'parent': response.request.meta['parent']},
                          callback=self.page_of_thread_list)
            reqs.append(req)
        return reqs

    def page_of_thread_list(self, response):
        """
        Crawl a specific paged thread list to get a list of threads.
        """
        hxs = HtmlXPathSelector(response)
        import ipdb; ipdb.set_trace();
        threads = hxs.select('')
        items_and_reqs = []
        for thr_selector in threads:
            thr_load = ThreadLoader(ThreadItem(), thr_selector)
            thr_load.add_xpath('zeta_id', '')
            thr_load.add_value('user', self.get_user())
            thr_load.add_value('forum', response.request.meta['parent'])
            thr_load.add_xpath('title', '')
            thr_load.add_xpath('subtitle', '')
            thr_load.add_xpath('replies', '')
            thr_load.add_xpath('view', '')
            thr_load.add_xpath('date_posted', '')
            thr = thr_load.load_item()
            items_and_reqs.append(thr)
            req = Request(thr_selector.select('').extract()[0],
                          meta={'parent': thr['zeta_id']},
                          callback=self.post_list)
            items_and_reqs.append(req)
        return items_and_reqs


SPIDER = ZetaboardsSpider()
