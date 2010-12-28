# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html
from library.models import Price, Shop
from scraper.items import BookItem


class SaveBookPricePipeline(object):
    """
    Take in BookItems and saves them to DB using the Django ORM.
    """

    def process_item(self, item, spider):
        if isinstance(item, BookItem):
            book = item['book']
            shop = Shop.objects.get(url__icontains=spider.name)
            if item.get('price'):
                # Price is set, so save.
                price = Price.objects.create(
                                book=book, 
                                shop=shop,
                                native_currency=item['currency'],
                                native_price=item['price'],
                                native_delivery=item['delivery'],
                                url=item['url'])
            else:
                # No price, some error occurred, set and save.
                error = item['error'] if item.has_key('error') else Price.UNKNOWN
                price = Price.objects.create(
                                book=book, 
                                shop=shop, 
                                native_currency=item['currency'],
                                error=error, 
                                url=item['url'])
            return item
        return None
