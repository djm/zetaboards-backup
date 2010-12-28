from django.contrib import admin
from library.models import Book, CurrencyTable, Price, Shop


class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'isbn', 'active']
    list_editable = ['active']
    list_filter = ['active']
    save_on_top = True
    search_fields = ['isbn', 'title']

class CurrencyTableAdmin(admin.ModelAdmin):
    list_display = ['from_currency', 'to_currency', 'rate']
    list_filter = ['from_currency', 'to_currency']
    save_on_top = True


class PriceAdmin(admin.ModelAdmin):
    list_display = ['shop', 'book', 'url_anchor', 'native_currency', 'native_price',
            'native_delivery', 'native_total', 'converted_currency', 
            'converted_price', 'converted_delivery', 'converted_total', 'error', 
            'date_added']
    list_filter = ['error']
    save_on_top = True
    search_fields = ['shop__name', 'book__isbn', 'book__title']


class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'short_name', 'delivery', 'featured', 
            '_last_scraped', 'active']
    list_editable = ['featured', 'active']
    save_on_top = True
    search_fields = ['name', 'url']


admin.site.register(Book, BookAdmin)
admin.site.register(CurrencyTable, CurrencyTableAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Shop, ShopAdmin)
