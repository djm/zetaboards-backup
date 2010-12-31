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
MEMBERS_PATH = getattr(settings, 'ZETABOARDS_MEMBERS_PATH', '/members/')


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
        We're going to grab the member list first, followed
        by getting the root categories from the index.
        """
        
        member_req = Request("%s%s" % (BOARD_URL, MEMBERS_PATH),
                             callback=self.members_list)
        index_req = Request(BOARD_URL, callback=self.root_index)
        return [member_req, index_req]

    def members_list(self, response):
        """
        Works out if we need to go into paginated members listing pages.
        """
        hxs = HtmlXPathSelector(response)
        last_page = hxs.select('//ul[@class="cat-pages"]/li[last()]/a/text()')
        if last_page:
            last_page = last_page.extract()[0]
            page_range = range(1, int(last_page)+1)
            reqs = []
            for page in page_range:
                req = Request("%s%i/" % (response.url, page),
                              callback=self.page_of_members_list)
                reqs.append(req)
            return reqs
        else:
            # There is just the one members list page.
            # We're already on the index so we don't
            # need an extra request.
            return self.page_of_members_list(response)

    def page_of_members_list(self, response):
        """
        An individual page of the members listing.
        This parses and makes requests for each
        profile.
        """
        hxs = HtmlXPathSelector(response)
        members = hxs.select('//a[@class="member"]/@href').extract()
        reqs = []
        for member_url in members:
            req = Request(member_url, callback=self.member_profile)
            reqs.append(req)
        return reqs

    def member_profile(self, response):
        """
        This parses a profile page into a User.
        """
        hxs = HtmlXPathSelector(response)
        mem_load = UserLoader(UserItem(), response=response)        
        mem_load.add_value('zeta_id', unicode(response.url))
        mem_load.add_xpath('username', '//th[@class="l"]/text()')
        mem_load.add_xpath('user_group', '//dl[@class="user_info"]/dt[text()="Group:"]/following-sibling::dd/text()')
        mem_load.add_xpath('member_number', '//dl[@class="user_info"]/dt[text()="Member"]/following-sibling::dd/text()')
        mem_load.add_xpath('post_count', '//dl[@class="user_info"]/dt[text()="Posts:"]/following-sibling::dd/text()')
        mem_load.add_xpath('signature', '//td[@class="c_sig"]/node()')
        date_birthday = mem_load.get_xpath('//td[text()="Birthday:"]/following-sibling::td/text()')
        mem_load.add_value('date_birthday', date_birthday)
        mem_load.add_xpath('date_joined', '//dl[@class="user_info"]/dt[text()="Joined:"]/following-sibling::dd/text()')
        return mem_load.load_item()

    def root_index(self, response):
        """
        Crawl the main index to get all root categories.
        """
        import ipdb; ipdb.set_trace();
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
        threads = hxs.select('//table[@class="posts"]/tr[contains(@class, "row1") or contains(@class, "row2")]')
        items_and_reqs = []
        for thr_selector in threads:
            thr_load = ThreadLoader(ThreadItem(), thr_selector)
            thr_load.add_xpath('zeta_id', 'td[@class="c_cat-title"]/a/@href')
            user_href = thr_selector.select('td[@class="c_cat-starter"]/a/@href').extract()[0]
            thr_load.add_value('user', self.get_user(user_href))
            thr_load.add_value('forum', response.request.meta['parent'])
            thr_load.add_xpath('title', 'td[@class="c_cat-title"]/a/text()')
            thr_load.add_xpath('subtitle', 'td[@class="c_cat-title"]/div[@class="description"]/text()')
            thr_load.add_xpath('replies', 'td[@class="c_cat-replies"]/a/text()')
            thr_load.add_xpath('view', 'td[@class="c_cat-views"]/text()')
            thr_load.add_xpath('date_posted', 'td[@class="c_cat-lastpost"]/div[@class="t_lastpostdate"]/text()')
            thr = thr_load.load_item()
            items_and_reqs.append(thr)
            req = Request(thr_selector.select('').extract()[0],
                          meta={'parent': thr['zeta_id']},
                          callback=self.post_list)
            items_and_reqs.append(req)
        return items_and_reqs


SPIDER = ZetaboardsSpider()
