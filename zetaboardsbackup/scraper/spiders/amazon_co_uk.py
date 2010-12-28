from scrapy.http import Request, FormRequest
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

from scraper.items import BookItem
from scraper.loader import BookLoader

from library.models import GBP, Book, Price, Shop

class AmazonCoUkSpider(BaseSpider):
    name = 'amazon.co.uk'
    books = Book.objects.all()
    shop = Shop.objects.get(name__iexact=name)

    def start_requests(self):
        request_list = []
        for book in self.books:
            form_request = FormRequest("http://www.amazon.co.uk/s/ref=nb_sb_noss",
                    formdata={
                        'url': 'search-alias=stripbooks',
                        'field-keywords': book.isbn},
                    callback=self.request_complete,
                    meta={'book': book}
                    )
            request_list.append(form_request)
        return request_list

    def request_complete(self, response):
        x = HtmlXPathSelector(response)
        href = x.select('//div[@id="result_0"]//div[@class="productTitle"]//a//@href').extract()
        if href:
            href = href[0]
            return Request(href, meta={'book': response.request.meta['book']})
        pass

    def parse(self, response):
        l = BookLoader(item=BookItem(book=response.request.meta['book']), 
                response=response)
        price = l.get_xpath('//table[@class="twisterMediaMatrix"]//tr[@class="activeRow bucketBorderTop"]//td[@class="price"]/text()')
        if price:
            l.add_value('price', price)
        else:
            l.add_value('error', Price.PRICE_UNAVAILABLE)
        l.add_value('delivery', unicode(self.shop.delivery))
        l.add_value('url', unicode(response.url))
        l.add_value('currency', GBP)
        return l.load_item()

SPIDER = AmazonCoUkSpider()
