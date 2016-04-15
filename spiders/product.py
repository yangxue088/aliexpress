# -*- coding: utf-8 -*-
import json
import logging
import urlparse
from datetime import datetime

import scrapy
from pybloom import ScalableBloomFilter
from scrapy_redis.spiders import RedisSpider

from items import UrlItem, ProductItem


class ProductSpider(RedisSpider):
    name = "product"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    def __init__(self):
        self.redis_key = 'ali:product:url'
        self.filter = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)

        self.products = dict()

    def start_requests(self):
        yield self.next_request()

    def parse(self, response):
        self.log('product url: {}'.format(response.url), logging.INFO)

        store_url = response.css('.shop-name').xpath('a/@href').extract()[0]
        self.log('crawl store url: {}'.format(store_url), logging.INFO)

        item = UrlItem()
        item['type'] = 'store'
        item['url'] = store_url
        yield item

        self.product(response.url).store = store_url

        feedback_base_url = response.xpath('//div[@id="feedback"]/iframe/@thesrc').extract()[0]
        yield self.request_feedback(response.url, feedback_base_url)

        parsed = urlparse.urlparse(feedback_base_url)
        product_id = urlparse.parse_qs(parsed.query)['productId'][0]
        yield self.request_order(response.url, product_id)

    def request_order(self, product_url, product_id, page=1):
        order_url = 'http://feedback.aliexpress.com/display/evaluationProductDetailAjaxService.htm?productId={}&type=default&page={}'.format(
            product_id, page)

        self.log('request order page: {}'.format(order_url), logging.INFO)

        return scrapy.Request(url=order_url, meta={'product_url': product_url, 'product_id': product_id, 'page': page},
                              callback=self.parse_order)

    def parse_order(self, response):
        orders = json.loads(response.body)

        records = [record for record in orders['records'] if not self.filter.add(record['id'])]

        if len(records) > 0:
            for record in records:
                date = datetime.strptime(record['date'], '%d %b %Y %H:%M')
                quantity = record['quantity']
                buyer_level = record['buyerAccountPointLeval']

                self.product(response.meta['product_url']).append_order(**{'date': date, 'quantity': quantity, 'buyer_level': buyer_level})

            return self.request_order(response.meta['product_url'], response.meta['product_id'], int(response.meta['page']) + 1)
        else:
            self.product(response.meta['product_url']).finish_order = True
            return self.pop_product(response.meta['product_url'])

    def request_feedback(self, product_url, feedback_base_url, page=1):
        feedback_url = '{}&page={}'.format(feedback_base_url, page)

        self.log('request feedback page: {}'.format(feedback_url), logging.INFO)

        return scrapy.Request(url=feedback_url, meta={'product_url': product_url, 'base_url': feedback_base_url, 'page': page},
                              callback=self.parse_feedback)

    def parse_feedback(self, response):
        feedback_items = response.css('.feedback-item')
        if len(feedback_items) > 0:
            for feedback_item in feedback_items:
                time = datetime.strptime(feedback_item.css('.r-time').xpath('text()').extract()[0], '%d %b %Y %H:%M')
                color = ''.join(feedback_item.css('.first').xpath('text()').extract()).strip()
                star_width = feedback_item.css('.star-view').xpath('span/@style').extract()[0]
                star = int(star_width[star_width.index(':') + 1:-1]) / 20

                self.product(response.meta['product_url']).append_feedback(time=time, color=color, star=star)

            return self.request_feedback(response.meta['product_url'], response.meta['base_url'], int(response.meta['page']) + 1)
        else:
            self.product(response.meta['product_url']).finish_feedback = True
            return self.pop_product(response.meta['product_url'])

    def product(self, url):
        if url not in self.products:
            self.products[url] = Product(url=url)
        return self.products[url]

    def pop_product(self, url):
        if self.product(url).is_finish():
            product = self.products.pop(url)

            assert product is not None
            assert product.url != ''

            self.log('crawl product: {}'.format(product))

            item = ProductItem()
            item['_id'] = product.url
            item['store'] = product.store
            item['url'] = product.url
            item['orders'] = product.orders
            item['feedbacks'] = product.feedbacks
            return item


class Product(object):
    def __init__(self, url):
        self.store = ''
        self.url = url
        self.orders = list()
        self.feedbacks = list()
        self.finish_order = False
        self.finish_feedback = False

    def append_order(self, **kwargs):
        self.orders.append(kwargs)

    def append_feedback(self, **kwargs):
        self.feedbacks.append(kwargs)

    def is_finish(self):
        return self.finish_order and self.finish_feedback

    def __str__(self):
        return 'product url: {}, orders: {}, feedbacks: {}'.format(self.url, len(self.orders), len(self.feedbacks))
