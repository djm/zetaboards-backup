import datetime
from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify

from library.managers import ActiveManager, PriceManager

GBP = 'GBP'
USD = 'USD'
EUR = 'EUR'
AUD = 'AUD'

CURRENCIES = (
    (GBP, _("GBP")),
    (USD, _("USD")),
    (EUR, _("EUR")),
    (AUD, _("AUD"))
)

# Want this to fail hard if it hasn't been set.
try:
    CONVERT_TO = settings.CONVERT_TO_CURRENCY
except AttributeError:
    raise AttributeError, "Please select a currency to convert to in the settings" \
                          " file by providing the `CONVERT_TO_CURRENCY` variable."

class Book(models.Model):
    """
    To define a book.
    """
    isbn = models.CharField(max_length=20, unique=True,
                            help_text="Used to lookup the book")
    title = models.CharField(max_length=255, help_text="Only used for display \
                             purposes")
    active = models.BooleanField(default=True, help_text="Actively crawl for \
                                 this book?")
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    all_objects = models.Manager()
    objects = ActiveManager()

    class Meta:
        ordering = ['title']

    def __unicode__(self):
        return u"%s [ISBN:%s]" % (self.title, self.isbn)

    def get_latest_price(self, shop, include_failed=True):
        """
        Given a shop instance, get the latest price instance for this book.
        """
        prices = self.price_set.filter(shop=shop)
        if not include_failed:
            prices = prices.exclude(error__isnull=False)
        prices = prices.order_by('-date_added')
        try:
            price = prices[0]
        except IndexError:
            price = None
        return price


class CurrencyTable(models.Model):
    """
    A simple currency conversion table.
    """
    from_currency = models.CharField(max_length=3, choices=CURRENCIES)
    to_currency = models.CharField(max_length=3, choices=CURRENCIES)
    rate = models.DecimalField(max_digits=10, decimal_places=6)

    class Meta:
        ordering = ['from_currency', 'to_currency']
        unique_together = ['from_currency', 'to_currency']

    def __unicode__(self):
        return u"%s => %s: %s" % (self.from_currency, self.to_currency, self.rate)

    @classmethod
    def get_rate(self, from_currency, to_currency=CONVERT_TO):
        """
        This methods accept the currency you are converting from and the 
        currency you are converting to (defaults to the one defined in settings)
        and tries to return the relevant rate from the table; if it fails, it will
        raise a hard exception.
        """
        try:
            row = self.objects.get(from_currency=from_currency,
                                   to_currency=to_currency)
        except self.DoesNotExist:
            raise self.DoesNotExist, "The requested converstion rate is not" \
                            " available: %s => %s." % (from_currency, to_currency)
        else:
            return row.rate 


class Price(models.Model):
    """
    Historical price table.
    """
    PRICE_UNAVAILABLE, UNKNOWN = range(1, 3)
    ERROR_CHOICES = (
        (PRICE_UNAVAILABLE, _("Price Unavailable/Out of Stock")),
        (UNKNOWN, _("Unknown Retrieval Error"))
    )
    book = models.ForeignKey('library.Book')
    shop = models.ForeignKey('library.Shop')
    # Currency is set here and not on the shop 
    # as some shops are multi-currency.
    native_currency = models.CharField(max_length=3, choices=CURRENCIES)
    native_price = models.DecimalField(max_digits=10, decimal_places=2,
                                null=True, blank=True)
    native_delivery = models.DecimalField(max_digits=10, decimal_places=2,
                                null=True, blank=True)
    _native_total = models.DecimalField(max_digits=10, decimal_places=2,
                                null=True, blank=True, editable=False)
    _converted_currency = models.CharField(max_length=3, choices=CURRENCIES, 
                                editable=False)
    _converted_price = models.DecimalField(max_digits=10, decimal_places=2,
                                null=True, blank=True, editable=False)
    _converted_delivery = models.DecimalField(max_digits=10, decimal_places=2,
                                null=True, blank=True, editable=False)
    _converted_total = models.DecimalField(max_digits=10, decimal_places=2,
                                null=True, blank=True, editable=False)
    error = models.IntegerField(choices=ERROR_CHOICES, null=True, blank=True)
    url = models.URLField(verify_exists=False)
    date_added = models.DateTimeField(default=datetime.datetime.now)

    all_objects = models.Manager()
    # By default, only return those prices whose converted
    # price has been recorded as the current "home" currency
    # as set by CONVERT_TO_CURRENCY.
    objects = PriceManager()

    class Meta:
        ordering = ['-date_added']

    def __unicode__(self):
        return u"%s - %s @ %s" % (self.book, self.shop, 
                self.date_added.strftime("%Y-%m-%d"))

    def save(self, *args, **kwargs):
        if self.native_price and self.native_delivery:
            # Make sure we're dealing with Decimal objects, django does this
            # on save usually but as we're ahead of ourselves..
            self.native_price = Decimal(self.native_price)
            self.native_delivery = Decimal(self.native_delivery)
            self._native_total = self.native_price + self.native_delivery
            self.do_currency_conversion()
        super(Price, self).save(*args, **kwargs)

    def _calculate_conversions(self):
        rate = CurrencyTable.get_rate(self.native_currency)
        self._converted_price = self.native_price * rate
        self._converted_delivery = self.native_delivery * rate
        self._converted_total = self.native_total * rate

    def do_currency_conversion(self):
        """
        Convert prices to "home" currency and store
        the currency converted to. Only call if native
        prices have been set, check prior!
        """
        # Do we even have to convert?
        if self.native_currency == CONVERT_TO:
            self._converted_currency = self.native_currency
            self._converted_price = self.native_price
            self._converted_delivery = self.native_delivery
            self._converted_total = self.native_total
        else:
            # Why yes we do.
            self._converted_currency = CONVERT_TO
            self._calculate_conversions()

    @property
    def converted_currency(self):
        return self._converted_currency

    @property
    def converted_price(self):
        return self._converted_price

    @property
    def converted_delivery(self):
        return self._converted_delivery

    @property
    def converted_total(self):
        return self._converted_total

    @property
    def native_total(self):
        return self._native_total

    def url_anchor(self):
        return u'<a href="%s" title="on %s">On site</a>' % (self.url, self.shop)
    url_anchor.allow_tags = True
    url_anchor.short_description = ''


class Shop(models.Model):
    """
    To detail the various shops we shall be spidering.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, editable=False)
    url = models.URLField(max_length=255, verify_exists=False,
                          help_text="The root domain of the shop.")
    short_name = models.CharField(max_length=10)
    featured = models.BooleanField(default=False)
    delivery = models.FloatField(blank=True, null=True, help_text="For shops who \
            have a blanket shopping price for everything.")
    active = models.BooleanField(default=True)
    _last_scraped = models.DateTimeField("Last scraped", blank=True, null=True)

    all_objects = models.Manager()
    objects = ActiveManager()

    class Meta:
        ordering = ['-featured', 'name']

    def __unicode__(self):
        return u"%s" % self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Shop, self).save(*args, **kwargs)

    @property
    def last_scraped(self):
        if self._last_scraped:
            return self._last_scraped.strftime("%Y-%m-%d %H:%M")
        else:
            return "Never"
