# -*- coding: utf-8 -*-
from scrapy import optional_features
from scrapy.crawler import CrawlerProcess

from spiders.product import ProductSpider

optional_features.remove('boto')

process = CrawlerProcess({'DOWNLOAD_DELAY': 0, 'COOKIES_ENABLED': False, 'ITEM_PIPELINES': {
    'pipelines.ToRedisPipeline': 300,
    'pipelines.ToMongoPipeline': 400,
}, 'LOG_LEVEL': 'INFO'})

# process.crawl(CategorySpider, 'http://www.aliexpress.com/category/380230/phone-bags-cases.html')

process.crawl(ProductSpider)

# process.crawl(StoreSpider)

process.start()
