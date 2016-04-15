# -*- coding: utf-8 -*-
from pymongo import MongoClient
from scrapy_redis.pipelines import RedisPipeline

from items import UrlItem, ProductItem, StoreItem


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
