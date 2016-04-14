# -*- coding: utf-8 -*-
import json
import urlparse

import scrapy
from pybloom import ScalableBloomFilter


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    def __init__(self, url):
        self.url = url
        self.filter = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)

    def start_requests(self):
        yield self.make_requests_from_url(self.url)

    def parse(self, response):
        store_url = response.css('.shop-name').xpath('a/@href').extract()[0]
        print store_url

        feedback_base_url = response.xpath('//div[@id="feedback"]/iframe/@thesrc').extract()[0]
        yield self.request_feedback(feedback_base_url)

        parsed = urlparse.urlparse(feedback_base_url)
        product_id = urlparse.parse_qs(parsed.query)['productId'][0]
        yield self.request_order(product_id)

    def request_order(self, product_id, page=1):
        order_url = 'http://feedback.aliexpress.com/display/evaluationProductDetailAjaxService.htm?productId={}&type=default&page={}'.format(
            product_id, page)
        print 'order page: {}'.format(order_url)
        return scrapy.Request(url=order_url, meta={'product_id': product_id, 'page': page}, callback=self.parse_order)

    def parse_order(self, response):
        orders = json.loads(response.body)

        records = [record for record in orders['records'] if not self.filter.add(record['id'])]

        if len(records) > 0:
            for record in records:
                date = record['date']
                quantity = record['quantity']
                buyer_level = record['buyerAccountPointLeval']

                print 'order date: {}, quantity: {}, buyer_level: {}'.format(date, quantity, buyer_level)

            return self.request_order(response.meta['product_id'], int(response.meta['page']) + 1)

    def request_feedback(self, feedback_base_url, page=1):
        feedback_url = '{}&page={}'.format(feedback_base_url, page)
        print 'feedback page: {}'.format(feedback_url)
        return scrapy.Request(url=feedback_url, meta={'base_url': feedback_base_url, 'page': page}, callback=self.parse_feedback)

    def parse_feedback(self, response):
        feedback_items = response.css('.feedback-item')
        if len(feedback_items) > 0:
            for feedback_item in feedback_items:
                time = feedback_item.css('.r-time').xpath('text()').extract()[0]
                color = ''.join(feedback_item.css('.first').xpath('text()').extract()).strip()

                star_width = feedback_item.css('.star-view').xpath('span/@style').extract()[0]
                star = int(star_width[star_width.index(':') + 1:-1]) / 20

                # print 'feedback time: {}, star: {}, color: {}'.format(time, star, color)

            return self.request_feedback(response.meta['base_url'], int(response.meta['page']) + 1)
