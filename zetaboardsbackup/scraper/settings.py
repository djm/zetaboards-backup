BOT_NAME = 'scraper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
DEFAULT_ITEM_CLASS = 'scraper.items.BookItem'
ITEM_PIPELINES = ['scraper.pipelines.SaveBookPricePipeline']

USER_AGENT = 'Googlebot/2.1 (+http://www.google.com/bot.html)'

# Connection Related Settings
CONCURRENT_REQUESTS_PER_SPIDER = 1
CONCURRENT_SPIDERS = 1
DOWNLOAD_DELAY = 15
RANDOMIZE_DOWNLOAD_DELAY = True

# For server safety
MEMUSAGE_LIMIT_MB = 200 # MB
MEMUSAGE_NOTIFY_LIMIT = ['django-alerts@tangentone.co.uk']

TELNETCONSOLE_ENABLED = False

try:
    from settings_local import *
except:
    pass
