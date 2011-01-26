from __future__ import division
import re

from BeautifulSoup import BeautifulSoup
from scrapy import log
from scrapy.conf import settings
from scrapy.exceptions import NotConfigured
from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

from scraper.items import ForumItem, ThreadItem, PostItem, RawPostItem, UserItem
from scraper.loaders import extract_numbers, ForumLoader, ThreadLoader, PostLoader,\
                            RawPostLoader, UserLoader

from forum.models import User

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
        Examine the root index.
        """
        return self.root_index(response)

    def get_member_if_required(self, url):
        zeta_id = extract_numbers(url)
        try:
            user = User.objects.get(pk=zeta_id)
        except User.DoesNotExist:
            return Request(url, callback=self.member_profile, priority=100)
        else:
            return None

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
                          meta={'forum': cat['zeta_id']},
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
                          meta={'forum': response.request.meta['forum']},
                          callback=self.page_of_thread_list)
            reqs.append(req)
        self.log("%s -> %i pages of threads." % (response.url, len(reqs)), level=log.INFO)
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
            user = self.get_member_if_required(thr_selector.select('td[@class="c_cat-starter"]/a/@href').extract()[0])
            if user:
                items_and_reqs.append(user)
            thr_load.add_xpath('user', 'td[@class="c_cat-starter"]/a/text()')
            thr_load.add_value('forum', response.request.meta['forum'])
            thr_load.add_xpath('title', 'td[@class="c_cat-title"]/a/text()')
            thr_load.add_xpath('subtitle', 'td[@class="c_cat-title"]/div[@class="description"]/text()')
            thr_load.add_xpath('replies', 'td[@class="c_cat-replies"]/a/text()')
            thr_load.add_xpath('views', 'td[@class="c_cat-views"]/text()')
            thr_load.add_xpath('date_posted', 'td[@class="c_cat-title"]/a/@title')
            thr = thr_load.load_item()
            items_and_reqs.append(thr)
            url = thr_selector.select('td[@class="c_cat-title"]/a/@href').extract()[0]
            # We have to deliberately go the first page, else it sends us to the last
            # page by default, hence appending the 1/.
            req = Request("%s1/" % url,
                          meta={
                              'forum': response.request.meta['forum'],
                              'thread': thr['zeta_id'],
                              'base_url': url
                              },
                          callback=self.post_list)
            items_and_reqs.append(req)
        self.log("%s -> %i items." % (response.url, len(items_and_reqs)), level=log.ERROR)
        return items_and_reqs

    def post_list(self, response):
        """
        Calculate the number of pages in thread and return
        a request for each page so that we can grab the posts.
        """
        hxs = HtmlXPathSelector(response)
        # We now need to work out how many pages are in this topic, if more than one.
        try:
            last_page = hxs.select('//ul[@class="cat-pages"]/li[last()]/a/text()').extract()[0]
            page_range = range(1, int(last_page)+1)
        except IndexError:
            # Then we couldn't find a pagination list, 
            # so we only have one page.
            return self.page_of_post_list(response)
        reqs = []
        base_thread_url = response.request.meta['base_url']
        for page in page_range:
            url = "%s%i/" % (base_thread_url, page)
            req = Request(url, meta={
                                  'forum': response.request.meta['forum'],
                                  'thread': response.request.meta['thread']},
                          callback=self.page_of_thread_list)
            self.log("Sending to %s" % url, level=log.ERROR)
            reqs.append(req)
        return reqs

    def page_of_post_list(self, response):
        """
        Parse a page of topic posts. Uses Beautiful soup so we 
        can easily do a regex lookup on the table row class names.
        """
        self.log("Receiving from %s" % response.url, level=log.ERROR)
        soup = BeautifulSoup(response.body)
        posts = soup.findAll('tr', id=re.compile("post-"))
        items_and_reqs = []
        for post in posts:
            # Load up and sort out BeautifulSoup stuff.
            post_loader = PostLoader(PostItem(), response=response)
            username = post.find('a', attrs={'class': 'member'})
            post_info = post.find('td', attrs={'class': 'c_postinfo'})
            raw_post = post.findNextSibling('tr').find('td', attrs={'class': 'c_post'}).text

            post_loader.add_value('thread', response.request.meta['thread'])
            post_loader.add_value('zeta_id', post['id'])
            post_loader.add_value('username', username.text)
            post_loader.add_value('ip_address', post_info.find('span', attrs={'class': 'desc'}).text)
            post_loader.add_value('date_posted', post_info.find('span', attrs={'class': 'left'}).text)
            post_item = post_loader.load_item()
            self.log(post_item, level=log.ERROR)
            items_and_reqs.append(post_item)
            edit_url = post.findNextSibling('tr', attrs={'class': 'c_postfoot'}).find('span', attrs={'class': 'left'}).find('a')['href']
            req = Request(edit_url,
                    meta={'forum': response.request.meta['forum'],
                          'thread': response.request.meta['thread'],
                          'post': post_item['zeta_id']},
                          callback=self.individual_post,
                          priority=-20)
            #items_and_reqs.append(req)
        self.log("%s -> %i items. %s" % (response.url, len(items_and_reqs), items_and_reqs), level=log.ERROR)
        return items_and_reqs

    def individual_post(self, response):
        """
        We visit the edit page for each post so we can grab the raw BBcode.
        """
        post_load = RawPostLoader(RawPostItem(), response=response)
        post_load.add_value('zeta_id', response.request.meta['post'])
        post_load.add_value('thread', response.request.meta['thread'])
        post_load.add_xpath('raw_post_bbcode', '//textarea[@id="c_post-text"]/text()')
        return post_load.load_item()

SPIDER = ZetaboardsSpider()

      #  if int(response.request.meta['thread']) in [8609396, 8607143, 8599241, 8553459, 8548529, 8540033, 8536013, 8504163, 572270, 572267, 572234, 572233, 572208, 572202, 572196, 572194, 572192, 572184, 572181, 572169, 572152, 572151, 572144, 572143, 572128, 572112, 572110, 572106, 572104, 572093, 572087, 572084, 572080, 572078, 572074, 572070, 572067, 572066, 572065, 572052, 572044, 572037, 572036, 572031, 572023, 572015, 572011, 572010, 572005, 572003, 571998, 571997, 571994, 571992, 571988, 571986, 571985, 571979]:
    #        import ipdb; ipdb.set_trace();
