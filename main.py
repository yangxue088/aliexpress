# -*- coding: utf-8 -*-

from scrapy import optional_features
from scrapy.crawler import CrawlerProcess

from spiders.feedback import FeedbackSpider
from spiders.order import OrderSpider
from spiders.product import ProductSpider

optional_features.remove('boto')

settings = {'DOWNLOAD_DELAY': 0, 'COOKIES_ENABLED': False, 'ITEM_PIPELINES': {
    'pipelines.DuplicatePipeline': 200,
    'pipelines.ToRedisPipeline': 300,
    'pipelines.ToMongoPipeline': 400,
}, 'LOG_LEVEL': 'INFO', 'prefix': 'phonebagscases',
            'base_url': 'http://www.aliexpress.com/category/380230/phone-bags-cases.html'}

process = CrawlerProcess(settings)
# process.crawl(CategorySpider)
process.crawl(ProductSpider)

# process.crawl(FeedbackSpider)
# process.crawl(OrderSpider)

# process.crawl(StoreSpider)

process.start()
