# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UrlItem(scrapy.Item):
    type = scrapy.Field()

    url = scrapy.Field()


class ProductItem(scrapy.Item):
    _id = scrapy.Field()

    store = scrapy.Field()

    url = scrapy.Field()

    orders = scrapy.Field()

    feedbacks = scrapy.Field()


class StoreItem(scrapy.Item):
    _id = scrapy.Field()

    url = scrapy.Field()

    name = scrapy.Field()

    positive_feedback = scrapy.Field()

    positive_score = scrapy.Field()

    since_time = scrapy.Field()

    one_month_feedback = scrapy.Field()

    three_month_feedback = scrapy.Field()

    six_month_feedback = scrapy.Field()

    twelve_month_feedback = scrapy.Field()

    overall_feedback = scrapy.Field()
