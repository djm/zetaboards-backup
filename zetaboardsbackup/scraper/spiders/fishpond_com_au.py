from scrapy.http import Request
from scrapy.spider import BaseSpider

from scraper.items import BookItem
from scraper.loader import BookLoader

from library.models import AUD, Book, Price, Shop

class FishpondComAuSpider(BaseSpider):
    name = 'fishpond.com.au'
    books = Book.objects.all()
    shop = Shop.objects.get(name__iexact=name)

    def start_requests(self):
        request_list = []
        for book in self.books:
            request = Request(
                    "http://www.fishpond.com.au/Books/%s/" % book.isbn,
                    meta={'book': book})
            request_list.append(request)
        return request_list

    def parse(self, response):
        l = BookLoader(item=BookItem(book=response.request.meta['book']), 
                response=response)
        price = l.get_xpath('//td[@class="product_info_text"]//span[@class="productSpecialPrice"]')
        if price:
            l.add_value('price', price)
        else:
            l.add_value('error', Price.PRICE_UNAVAILABLE)
        l.add_value('delivery', unicode(self.shop.delivery))
        l.add_value('url', response.url)
        l.add_value('currency', AUD)
        return l.load_item()

SPIDER = FishpondComAuSpider()
