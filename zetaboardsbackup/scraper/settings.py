BOT_NAME = 'scraper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['scraper.spiders']
NEWSPIDER_MODULE = 'scraper.spiders'
ITEM_PIPELINES = ['scraper.pipelines.ZetaboardsPipeline']

# THIS IS KEY. SETTING IT TO CONTAIN `GOOGLEBOT` WILL NOT ALLOW YOU TO LOG IN.
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.04 (lucid) Firefox/3.6.13'

# Connection Related Settings
CONCURRENT_REQUESTS_PER_SPIDER = 4
CONCURRENT_SPIDERS = 4
#DOWNLOAD_DELAY = 15
#RANDOMIZE_DOWNLOAD_DELAY = True

# To remove the compression middleware default, zetaboards seems to have
# issues with some pages not being properly gzipped.
DOWNLOADER_MIDDLEWARES_BASE = {
    'scrapy.contrib.downloadermiddleware.robotstxt.RobotsTxtMiddleware': 100,
    'scrapy.contrib.downloadermiddleware.httpauth.HttpAuthMiddleware': 300,
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.retry.RetryMiddleware': 500,
    'scrapy.contrib.downloadermiddleware.defaultheaders.DefaultHeadersMiddleware': 550,
    'scrapy.contrib.downloadermiddleware.redirect.RedirectMiddleware': 600,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': 700,
    'scrapy.contrib.downloadermiddleware.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.contrib.downloadermiddleware.stats.DownloaderStats': 850,
    'scrapy.contrib.downloadermiddleware.httpcache.HttpCacheMiddleware': 900,
}

EXTENSIONS = {
    'scraper.extensions.SpiderCloseFunctionality': 500,
}

try:
    from settings_local import *
except:
    pass
