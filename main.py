# -*- coding: utf-8 -*-

from scrapy import optional_features
from scrapy.crawler import CrawlerProcess

from spiders.category import CategorySpider

optional_features.remove('boto')

settings = {'COOKIES_ENABLED': False, 'ITEM_PIPELINES': {
    'pipelines.DuplicatePipeline': 200,
    'pipelines.ToRedisPipeline': 300,
    'pipelines.ToMongoPipeline': 400,
}, 'LOG_LEVEL': 'INFO', 'prefix': 'searchusbinusbflashdrivers',
            'base_url': 'http://www.aliexpress.com/wholesale?catId=711005&SearchText=usb',
            # 'DOWNLOADER_MIDDLEWARES': {'scrapy_crawlera.CrawleraMiddleware': 600},
            # 'CRAWLERA_ENABLED': True,
            # 'CRAWLERA_USER': '29935fa9eb5c404985b6ad6cacc6a30e',
            # 'CRAWLERA_PASS': '',
            # 'CONCURRENT_REQUESTS': 10,
            # 'CONCURRENT_REQUESTS_PER_DOMAIN': 10,
            # 'AUTOTHROTTLE_ENABLED': False,
            # 'DOWNLOAD_TIMEOUT': 600
            }

process = CrawlerProcess(settings)
process.crawl(CategorySpider)
# process.crawl(ProductSpider)
# process.crawl(FeedbackSpider)
# process.crawl(OrderSpider)
# process.crawl(StoreSpider)

process.start()
