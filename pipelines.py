# -*- coding: utf-8 -*-
from pymongo import MongoClient
from scrapy_redis.pipelines import RedisPipeline

from items import UrlItem, ProductItem, StoreItem


class ToRedisPipeline(RedisPipeline):
    def process_item(self, item, spider):
        if isinstance(item, UrlItem):
            self.server.rpush('ali:{}:url'.format(item['type']), item['url'])
        return item


class ToMongoPipeline(object):
    def __init__(self):
        self.db = MongoClient().aliexpress

    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            self.db['products'].insert_one(item)
        elif isinstance(item, StoreItem):
            self.db['stores'].insert_one(item)
        return item
