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
        if not isinstance(item, UrlItem) and self.filter.add('{}{}'.format(spider.name, item['_id'])):
            raise DropItem('duplicate item found, spider name: {}, for: {}'.format(spider.name, item['_id']))
        else:
            return item


class ToRedisPipeline(RedisPipeline):
    def process_item(self, item, spider):
        if isinstance(item, UrlItem):
            self.server.rpush(item.queue(), item['url'])
        return item


class ToMongoPipeline(object):
    def __init__(self):
        self.db = MongoClient().aliexpress

    def process_item(self, item, spider):
        if isinstance(item, ProductItem) or isinstance(item, StoreItem) or isinstance(item, FeedbackItem) or isinstance(item, OrderItem):
            self.db[item.queue()].insert_one(item)
        return item
