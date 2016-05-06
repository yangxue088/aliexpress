# -*- coding: utf-8 -*-
import logging
import urlparse
from datetime import datetime

import scrapy
from pybloom import ScalableBloomFilter
from pymongo import MongoClient
from scrapy.exceptions import CloseSpider
from scrapy_redis.spiders import RedisSpider

from items import StoreFeedbackItem


class StoreFeedbackSpider(RedisSpider):
    name = "store"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    prefix = ''

    def __init__(self):
        self.feedbacks = dict()
        self.redis_queue = None
        self.ids = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)

    def get_queue(self):
        for value in set(self.server.smembers(self.redis_key)):
            yield value

    def start_requests(self):
        StoreFeedbackSpider.prefix = self.settings['prefix']
        self.redis_key = '{}:storefeedback'.format(StoreFeedbackSpider.prefix)

        self.redis_queue = self.get_queue()

        db = MongoClient().aliexpress
        for store_feedback in db['{}storefeedback'.format(StoreFeedbackSpider.prefix)].find():
            self.ids.add(store_feedback['id'])

        yield self.next_request()

    def next_request(self):
        while True:
            try:
                url = next(self.redis_queue)
            except StopIteration:
                url = None

            if not (url and self.ids.add(urlparse.parse_qs(urlparse.urlparse(url).query)['storeId'][0])):
                break

        if url:
            return self.make_requests_from_url(url)
        else:
            raise CloseSpider('redis queue has no url to request')

    def make_requests_from_url(self, url):
        self.log('request store feedback url: {}'.format(url), logging.INFO)
        parsed = urlparse.urlparse(url)
        store_id = urlparse.parse_qs(parsed.query)['storeId'][0]
        return self.request(store_id, url)

    def request(self, store_id, base_url, page=1):
        feedback_url = '{}&page={}'.format(base_url, page)
        self.log('request store feedback page: {}'.format(feedback_url), logging.INFO)

        return scrapy.Request(url=feedback_url, meta={'store_id': store_id, 'base_url': base_url, 'page': page},
                              callback=self.parse)

    def parse(self, response):
        self.log('parse store feedback page: {}'.format(response.url), logging.INFO)

        trs = response.xpath('//tbody/tr')
        if len(trs) > 0:
            for tr in trs:
                product = tr.css('.product-name').xpath('a/@href').extract()[0].replace('//', '/')
                time = datetime.strptime(tr.css('.feedback-date').xpath('text()').extract()[0], '%d %b %Y %H:%M')
                star_width = tr.css('.star').xpath('span/@style').extract()[0]
                star = int(star_width[star_width.index(':') + 1:-2]) / 20

                self.store(response.meta['store_id']).append_feedback(time=time, product=product, star=star)

            return self.request(response.meta['store_id'], response.meta['base_url'], int(response.meta['page']) + 1)
        else:
            self.store(response.meta['store_id']).finish_feedback = True
            return self.pop_feedback(response.meta['store_id'])

    def store(self, id):
        if id not in self.feedbacks:
            self.feedbacks[id] = StoreFeedback(id)
        return self.feedbacks[id]

    def pop_feedback(self, id):
        if self.store(id).is_finish():
            feedback = self.feedbacks.pop(id)

            self.log('crawl store feedback: {}'.format(feedback), logging.INFO)

            item = StoreFeedbackItem()
            item['prefix'] = StoreFeedbackSpider.prefix
            item['_id'] = feedback.id
            item['feedbacks'] = feedback.feedbacks
            return item


class StoreFeedback(object):
    def __init__(self, id):
        self.id = id
        self.feedbacks = list()
        self.finish_feedback = False

    def append_feedback(self, **kwargs):
        self.feedbacks.append(kwargs)

    def is_finish(self):
        return self.finish_feedback

    def __str__(self):
        return 'store id: {}, feedbacks: {}'.format(self.id, len(self.feedbacks))
