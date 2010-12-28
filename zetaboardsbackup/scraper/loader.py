import re
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import Identity, TakeFirst, MapCompose

def extract_price(s):
    regex = re.compile("(?P<price>[0-9]{1,4}\.[0-9]{2})")
    r = regex.search(s)
    if r:
        return r.groups()[0]
    else:
        return None

class BookLoader(XPathItemLoader):

    default_output_processor = TakeFirst()

    url_in = Identity()
    currency_in = Identity()
    price_in = MapCompose(unicode.strip, extract_price)
    delivery_price_in = MapCompose(unicode.strip, extract_price)
    error_in = Identity()
