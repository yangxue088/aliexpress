# -*- coding: utf-8 -*-
from pybloom import ScalableBloomFilter
from pymongo import MongoClient
from scrapy.exceptions import DropItem
from scrapy_redis.pipelines import RedisPipeline

from items import UrlItem, ProductItem, StoreItem


class DuplicatePipeline(object):
    def __init__(self):
        self.urls = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)

    def process_item(self, item, spider):
        if isinstance(item, ProductItem) and self.urls.add(item['_id']):
            raise DropItem('duplicate item found, for: {}'.format(item['_id']))
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
        if isinstance(item, ProductItem) or isinstance(item, StoreItem):
            self.db[item.queue()].insert_one(item)
        return item
