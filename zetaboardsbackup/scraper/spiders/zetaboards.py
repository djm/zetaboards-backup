from scrapy.http import FormRequest
from scrapy.spider import BaseSpider

from scraper.items import BookItem
from scraper.loader import BookLoader

from library.models import AUD, Book, Price, Shop

class BordersComAuSpider(BaseSpider):
    name = 'borders.com.au'
    books = Book.objects.all()
    shop = Shop.objects.get(name__iexact=name)

    def start_requests(self):
        request_list = []
        for book in self.books:
            form_request = FormRequest("http://www.borders.com.au/search",
                    formdata={'query': book.isbn},
                    callback=self.request_complete,
                    meta={'book': book}
                    )
            request_list.append(form_request)
        return request_list

    def request_complete(self, response):
        # We submit a post request with the ISBN and expect
        # it to redirect to a book.
        if 'book' in response.url:
            return self.parse(response)
        else:
            return None

    def parse(self, response):
        l = BookLoader(item=BookItem(book=response.request.meta['book']), 
                response=response)
        price = l.get_xpath('//p[@class="price"]//b/text()')
        if price:
            l.add_value('price', price)
        else:
            l.add_value('error', Price.PRICE_UNAVAILABLE)
        l.add_value('delivery', unicode(self.shop.delivery))
        l.add_value('url', unicode(response.url))
        l.add_value('currency', AUD)
        return l.load_item()

SPIDER = BordersComAuSpider()
