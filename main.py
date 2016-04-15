# -*- coding: utf-8 -*-
from scrapy import optional_features
from scrapy.crawler import CrawlerProcess

from spiders.category import CategorySpider
from spiders.product import ProductSpider
from spiders.store import StoreSpider

optional_features.remove('boto')

process = CrawlerProcess({'DOWNLOAD_DELAY': 0, 'COOKIES_ENABLED': False, 'ITEM_PIPELINES': {
    'pipelines.ToRedisPipeline': 300,
    'pipelines.ToMongoPipeline': 400,
}, 'LOG_LEVEL': 'INFO', 'prefix': 'phone-bags-cases', 'base_url': 'http://www.aliexpress.com/category/380230/phone-bags-cases.html'})

process.crawl(CategorySpider)

for i in xrange(10):
    process.crawl(ProductSpider)

process.crawl(StoreSpider)

process.start()
