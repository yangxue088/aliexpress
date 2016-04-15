# -*- coding: utf-8 -*-
from scrapy import optional_features
from scrapy.crawler import CrawlerProcess

from spiders.product import ProductSpider
from spiders.store import StoreSpider

optional_features.remove('boto')

process = CrawlerProcess({'DOWNLOAD_DELAY': 0, 'COOKIES_ENABLED': False, 'ITEM_PIPELINES': {
    'pipelines.ToRedisPipeline': 300,
    'pipelines.ToMongoPipeline': 400,
}, 'LOG_LEVEL': 'INFO', 'HTTP_PROXY': 'http://127.0.0.1:8123',
                          'DOWNLOADER_MIDDLEWARES': {
                              'middlewares.RandomUserAgentMiddleware': 400,
                              'middlewares.ProxyMiddleware': 410,
                              'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None
                          }, 'USER_AGENT_LIST': [
        'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) Gecko/16.0 Firefox/16.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10']})

# process.crawl(CategorySpider, 'http://www.aliexpress.com/category/380230/phone-bags-cases.html')

process.crawl(ProductSpider)

# process.crawl(StoreSpider)

process.start()
