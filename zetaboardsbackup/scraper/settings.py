BOT_NAME = 'scraper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
ITEM_PIPELINES = ['scraper.pipelines.ZetaboardsPipeline']

# THIS IS KEY. SETTING IT TO CONTAIN `GOOGLEBOT` WILL NOT ALLOW YOU TO LOG IN.
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.04 (lucid) Firefox/3.6.13'

# Connection Related Settings
CONCURRENT_REQUESTS_PER_SPIDER = 1
CONCURRENT_SPIDERS = 1
#DOWNLOAD_DELAY = 15
#RANDOMIZE_DOWNLOAD_DELAY = True

try:
    from settings_local import *
except:
    pass
