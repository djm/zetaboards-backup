#!/usr/bin/env python
# encoding: utf-8
import random
import os
import subprocess
from datetime import datetime

from django.core.management.base import NoArgsCommand

from library.models import Shop

class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        print "Selecting shop to scrape..."
        # Get the 3 shops that have not been scraped for the
        # longest period of time. Then shuffle and pick one
        # to scrape, this adds a certain amount of randomness.
        shops = list(Shop.objects.all().order_by('_last_scraped')[:3])
        random.shuffle(shops)
        try:
            shop = shops[0]
            print "Selected shop: %s [Last Scraped: %s]" % (shop, shop.last_scraped) 
        except IndexError:
            raise Exception, "There do not seem to be any active shops to scrape."
        spider_name = shop.name.lower()
        print "Loading shop spider: %s" % spider_name
        try:
            subprocess.check_call(['/usr/local/bin/scrapy', 'crawl', spider_name])
        except subprocess.CalledProcessError:
            message = "%s crawler failed at %s." % (shop, 
                    datetime.now().strftime("%Y-%m-%d %H:%M"))
            print message
        else:
            shop._last_scraped = datetime.now()
            shop.save()
            print "Finished scraping. Till next time compadre.."
