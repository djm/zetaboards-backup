from scrapy.item import Item, Field

class BookItem(Item):
    """
    A model to represent a scraped book. If price is not set, then the error
    field should be set to one of the error choices (see library.models.Price)
    """
    book = Field()
    url = Field()
    currency = Field()
    price = Field()
    delivery = Field()
    error = Field()
