# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UrlItem(scrapy.Item):
    prefix = scrapy.Field()

    type = scrapy.Field()

    url = scrapy.Field()

    def queue(self):
        return '{}:{}'.format(self['prefix'], self['type'])


class ProductItem(scrapy.Item):
    prefix = scrapy.Field()

    _id = scrapy.Field()

    store = scrapy.Field()

    url = scrapy.Field()

    percent_num = scrapy.Field()

    rantings_num = scrapy.Field()

    order_num = scrapy.Field()

    def queue(self):
        return '{}product'.format(self['prefix'])


class FeedbackItem(scrapy.Item):
    prefix = scrapy.Field()

    _id = scrapy.Field()

    feedbacks = scrapy.Field()

    def queue(self):
        return '{}feedback'.format(self['prefix'])


class OrderItem(scrapy.Item):
    prefix = scrapy.Field()

    _id = scrapy.Field()

    orders = scrapy.Field()

    def queue(self):
        return '{}order'.format(self['prefix'])


class StoreItem(scrapy.Item):
    prefix = scrapy.Field()

    _id = scrapy.Field()

    url = scrapy.Field()

    name = scrapy.Field()

    product = scrapy.Field()

    positive_feedback = scrapy.Field()

    positive_score = scrapy.Field()

    since_time = scrapy.Field()

    one_month_feedback = scrapy.Field()

    three_month_feedback = scrapy.Field()

    six_month_feedback = scrapy.Field()

    twelve_month_feedback = scrapy.Field()

    overall_feedback = scrapy.Field()

    def queue(self):
        return '{}store'.format(self['prefix'])


class StoreFeedbackItem(scrapy.Item):
    prefix = scrapy.Field()

    _id = scrapy.Field()

    feedbacks = scrapy.Field()

    def queue(self):
        return '{}storefeedback'.format(self['prefix'])
