# -*- coding: utf-8 -*-
import logging
import urlparse
from datetime import datetime

import scrapy
from scrapy_redis.spiders import RedisSpider

from items import FeedbackItem


class FeedbackSpider(RedisSpider):
    name = "feedback"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    prefix = ''

    def __init__(self):
        self.feedbacks = dict()

    def start_requests(self):
        FeedbackSpider.prefix = self.settings['prefix']
        self.redis_key = '{}:feedback'.format(FeedbackSpider.prefix)

        yield self.next_request()

    def make_requests_from_url(self, url):
        self.log('request order page: {}'.format(url), logging.INFO)
        parsed = urlparse.urlparse(url)
        product_id = urlparse.parse_qs(parsed.query)['productId'][0]
        return self.request(product_id, url)

    def request(self, product_id, base_url, page=1):
        feedback_url = '{}&page={}'.format(base_url, page)
        return scrapy.Request(url=feedback_url, meta={'product_id': product_id, 'base_url': base_url, 'page': page},
                              callback=self.parse)

    def parse(self, response):
        feedback_items = response.css('.feedback-item')
        if len(feedback_items) > 0:
            for feedback_item in feedback_items:
                time = datetime.strptime(feedback_item.css('.r-time').xpath('text()').extract()[0], '%d %b %Y %H:%M')
                color = ''.join(feedback_item.css('.first').xpath('text()').extract()).strip()
                star_width = feedback_item.css('.star-view').xpath('span/@style').extract()[0]
                star = int(star_width[star_width.index(':') + 1:-1]) / 20

                self.product(response.meta['product_id']).append_feedback(time=time, color=color, star=star)

            return self.request(response.meta['product_id'], response.meta['base_url'], int(response.meta['page']) + 1)
        else:
            self.product(response.meta['product_id']).finish_feedback = True
            return self.pop_feedback(response.meta['product_id'])

    def product(self, id):
        if id not in self.feedbacks:
            self.feedbacks[id] = Feedback(id)
        return self.feedbacks[id]

    def pop_feedback(self, id):
        if self.product(id).is_finish():
            feedback = self.feedbacks.pop(id)

            self.log('crawl feedback: {}'.format(feedback), logging.INFO)

            item = FeedbackItem()
            item['prefix'] = FeedbackSpider.prefix
            item['_id'] = feedback.id
            item['feedbacks'] = feedback.feedbacks
            return item


class Feedback(object):
    def __init__(self, id):
        self.id = id
        self.feedbacks = list()
        self.finish_feedback = False

    def append_feedback(self, **kwargs):
        self.feedbacks.append(kwargs)

    def is_finish(self):
        return self.finish_feedback

    def __str__(self):
        return 'product id: {}, feedbacks: {}'.format(self.id, len(self.feedbacks))
