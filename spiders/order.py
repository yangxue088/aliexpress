# -*- coding: utf-8 -*-
import json
import logging
import urlparse
from datetime import datetime

import scrapy
from pybloom import ScalableBloomFilter
from scrapy_redis.spiders import RedisSpider

from items import OrderItem


class OrderSpider(RedisSpider):
    name = "order"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    prefix = ''

    def __init__(self):
        self.filter = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)
        self.orders = dict()

    def start_requests(self):
        OrderSpider.prefix = self.settings['prefix']
        self.redis_key = '{}:order'.format(OrderSpider.prefix)

        yield self.next_request()

    def make_requests_from_url(self, url):
        self.log('request order page: {}'.format(url), logging.INFO)
        parsed = urlparse.urlparse(url)
        product_id = urlparse.parse_qs(parsed.query)['productId'][0]
        return self.request(product_id, url)

    def request(self, product_id, base_url, page=1):
        order_url = '{}&page={}'.format(base_url, page)
        return scrapy.Request(url=order_url, meta={'product_id': product_id, 'base_url': base_url, 'page': page},
                              callback=self.parse)

    def parse(self, response):
        orders = json.loads(response.body.replace('\\', ''))
        records = [record for record in orders['records'] if not self.filter.add(record['id'])]

        if len(records) > 0:
            for record in records:
                date = datetime.strptime(record['date'], '%d %b %Y %H:%M')
                quantity = record['quantity']
                buyer_level = record['buyerAccountPointLeval']
                self.order(response.meta['product_id']).append_order(**{'date': date, 'quantity': quantity, 'buyer_level': buyer_level})

            return self.request(response.meta['product_id'], response.meta['base_url'], int(response.meta['page']) + 1)
        else:
            self.order(response.meta['product_id']).finish_order = True
            return self.pop_order(response.meta['product_id'])

    def order(self, id):
        if id not in self.orders:
            self.orders[id] = Order(id)
        return self.orders[id]

    def pop_order(self, id):
        if self.order(id).is_finish():
            order = self.orders.pop(id)

            self.log('crawl order: {}'.format(order), logging.INFO)

            item = OrderItem()
            item['prefix'] = OrderSpider.prefix
            item['_id'] = order.id
            item['orders'] = order.orders
            return item


class Order(object):
    def __init__(self, id):
        self.id = id
        self.orders = list()
        self.finish_order = False

    def append_order(self, **kwargs):
        self.orders.append(kwargs)

    def is_finish(self):
        return self.finish_order

    def __str__(self):
        return 'product id: {}, orders: {}'.format(self.id, len(self.orders))
