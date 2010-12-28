from django.conf import settings
from django.db import models

# Want this to fail hard if it hasn't been set.
try:
    CONVERT_TO = settings.CONVERT_TO_CURRENCY
except AttributeError:
    raise AttributeError, "Please select a currency to convert to in the settings" \
                          " file by providing the `CONVERT_TO_CURRENCY` variable."

class ActiveManager(models.Manager):

    def get_query_set(self):
        return super(ActiveManager, self).get_query_set().filter(active=True)

class PriceManager(models.Manager):

    def get_query_set(self):
        return super(PriceManager, self).get_query_set()\
                .filter(_converted_currency=CONVERT_TO)
