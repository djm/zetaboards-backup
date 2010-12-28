import time

from library.models import Price

def get_price_timeline(book, shop):
    """
    Given a book and a shop instance, returns a correctly formatted
    dataset ready to pass to the template and work with flot.
    """
    prices = Price.objects.filter(book=book, shop=shop).order_by('date_added')
    dataset = []
    for price in prices:
        timestamp = int(time.mktime(price.date_added.timetuple()))
        js_timestamp = timestamp * 1000
        dataset.append([js_timestamp, price.converted_price])
    return dataset
