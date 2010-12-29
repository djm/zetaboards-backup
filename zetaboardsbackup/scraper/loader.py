from scrapy.contrib.loader import XPathItemLoader
from scrapy.contrib.loader.processor import Identity, TakeFirst, MapCompose


class ForumLoader(XPathItemLoader):
    pass


class ThreadLoader(XPathItemLoader):
    pass


class PostLoader(XPathItemLoader):
    pass


class UserLoader(XPathItemLoader):
    pass


class UserGroupLoader(XPathItemLoader):
    pass
