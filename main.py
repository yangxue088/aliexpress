# -*- coding: utf-8 -*-

from scrapy import optional_features
from scrapy.crawler import CrawlerProcess

from spiders.feedback import FeedbackSpider
from spiders.order import OrderSpider
from spiders.product import ProductSpider
from spiders.store import StoreSpider

optional_features.remove('boto')

settings = {'COOKIES_ENABLED': False, 'ITEM_PIPELINES': {
    'pipelines.DuplicatePipeline': 200,
    'pipelines.ToRedisPipeline': 300,
    'pipelines.ToMongoPipeline': 400,
}, 'LOG_LEVEL': 'INFO', 'prefix': 'phonebagscases',
            'base_url': 'http://www.aliexpress.com/category/380230/phone-bags-cases.html',
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
# process.crawl(CategorySpider)
# process.crawl(ProductSpider)
process.crawl(FeedbackSpider)
process.crawl(OrderSpider)
process.crawl(StoreSpider)

process.start()
