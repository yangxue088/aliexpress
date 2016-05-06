# -*- coding: utf-8 -*-

from scrapy import optional_features
from scrapy.crawler import CrawlerProcess

from spiders.store_feedback import StoreFeedbackSpider

optional_features.remove('boto')

settings = {'TELNETCONSOLE_ENABLED': False, 'COOKIES_ENABLED': False, 'ITEM_PIPELINES': {
    'pipelines.DuplicatePipeline': 200,
    'pipelines.ToRedisPipeline': 300,
    'pipelines.ToMongoPipeline': 400,
}, 'LOG_LEVEL': 'INFO', 'prefix': 'test',
            'base_url': ''}

# first step
process = CrawlerProcess(settings)

process.crawl(StoreFeedbackSpider)

process.start()
