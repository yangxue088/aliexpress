# -*- coding: utf-8 -*-

from scrapy import optional_features
from scrapy.crawler import CrawlerProcess

from spiders.store import StoreSpider

optional_features.remove('boto')

settings = {'TELNETCONSOLE_ENABLED': False, 'COOKIES_ENABLED': False, 'ITEM_PIPELINES': {
    'pipelines.DuplicatePipeline': 200,
    'pipelines.ToRedisPipeline': 300,
    'pipelines.ToMongoPipeline': 400,
}, 'LOG_LEVEL': 'INFO', 'prefix': 'copyearphonesheadphones',
            'base_url': 'http://www.aliexpress.com/category/200003130/armbands.html'}

crawlera_settings = dict(settings)
crawlera_settings.update({'DOWNLOADER_MIDDLEWARES': {'scrapy_crawlera.CrawleraMiddleware': 600},
                          'CRAWLERA_ENABLED': True,
                          'CRAWLERA_USER': '29935fa9eb5c404985b6ad6cacc6a30e',
                          'CRAWLERA_PASS': '',
                          'CONCURRENT_REQUESTS': 10,
                          'CONCURRENT_REQUESTS_PER_DOMAIN': 10,
                          'AUTOTHROTTLE_ENABLED': False,
                          'DOWNLOAD_TIMEOUT': 10})

# process = CrawlerProcess(settings)
process = CrawlerProcess(crawlera_settings)

# process.crawl(CategorySpider, lambda rate, order: rate >= 100 or order >= 100)
# process.crawl(ProductSpider)
# for i in xrange(100):
#     process.crawl(FeedbackSpider)
#     process.crawl(OrderSpider)
# for i in xrange(2):
process.crawl(StoreSpider)

process.start()
