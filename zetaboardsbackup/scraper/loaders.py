import re
from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import TakeFirst, MapCompose

def extract_numbers(s):
    regex = re.compile("(?P<id>[0-9]+)")
    r = regex.search(s)
    if r:
        return r.groups()[0]
    else:
        return None

class ForumLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)


class ThreadLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)


class PostLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)


class UserLoader(XPathItemLoader):
    default_output_processor = TakeFirst()

    zeta_id_in = MapCompose(unicode.strip, extract_numbers)
    member_number_in = MapCompose(unicode.strip, extract_numbers)


class UserGroupLoader(XPathItemLoader):
    default_output_processor = TakeFirst()
