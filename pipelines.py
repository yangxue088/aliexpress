# -*- coding: utf-8 -*-
from pybloom import ScalableBloomFilter
from pymongo import MongoClient
from scrapy.exceptions import DropItem
from scrapy_redis.pipelines import RedisPipeline

from items import UrlItem, ProductItem, StoreItem, FeedbackItem, OrderItem


class DuplicatePipeline(object):
    def __init__(self):
        self.filter = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)

    def process_item(self, item, spider):
        if isinstance(item, UrlItem):
            uid = '{}{}{}'.format(spider.prefix, spider.name, item['url'])
        else:
            uid = '{}{}{}'.format(spider.prefix, spider.name, item['_id'])

        if self.filter.add(uid):
            raise DropItem('duplicate item found')
        else:
            return item


class ToRedisPipeline(RedisPipeline):
    def process_item(self, item, spider):
        if isinstance(item, UrlItem):
            self.server.sadd(item.queue(), item['url'])
        return item


class ToMongoPipeline(object):
    def __init__(self):
        self.db = MongoClient().aliexpress

    def process_item(self, item, spider):
        if isinstance(item, ProductItem) or isinstance(item, StoreItem) or isinstance(item, FeedbackItem) or isinstance(item, OrderItem):
            self.db[item.queue()].insert_one(item)
        return item
