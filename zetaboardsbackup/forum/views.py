from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.template import RequestContext
from django.shortcuts import render_to_response

from library.models import Book, Shop
from library.utils import get_price_timeline

import pprint
pp = pprint.PrettyPrinter()

# Want this to fail hard if it hasn't been set.
try:
    CONVERT_TO = settings.CONVERT_TO_CURRENCY
except AttributeError:
    raise AttributeError, "Please select a currency to convert to in the settings" \
                          " file by providing the `CONVERT_TO_CURRENCY` variable."

@staff_member_required
def price_grid(request):
    books = Book.objects.all()
    featured_shop = Shop.objects.get(featured=True)
    featured_prices = {}
    for book in books:
        featured_prices[book] = book.get_latest_price(featured_shop)
    other_shops = Shop.objects.exclude(featured=True)

    other_prices = []
    # This bit could definitely be bettered performance wise
    # but with time constraints and the fact it's on a VM
    # by itself and also not public - page view times are still
    # very quick. As the book count goes up this may however
    # need revisiting. #TODO
    for book in books:
        holder = []
        holder.append(book)
        price_holder = []
        for shop in other_shops:
            price_holder.append(book.get_latest_price(shop))
        holder.append(price_holder)
        other_prices.append(holder)
    context = {
            'converted_currency': CONVERT_TO,
            'featured_prices': featured_prices,
            'featured_shop': featured_shop,
            'other_prices': other_prices,
            'other_shops': other_shops,
            }
    return render_to_response('library/admin/price_grid.html',
                              context, RequestContext(request))

@staff_member_required
def price_graph(request, book, shop=None):
    book = Book.objects.get(id=book)
    datasets = {}
    if shop:
        # Then we only need to get the price data for
        # that one specified shop.
        shop = Shop.objects.get(id=shop)
        datasets[shop] = get_price_timeline(book, shop)
    else:
        # Else we get information for all shops.
        for shop in Shop.objects.all():
            datasets[shop] = get_price_timeline(book, shop)
    context = {'datasets': datasets, 'book': book}
    return render_to_response('library/admin/price_graph.html',
                              context, RequestContext(request))
