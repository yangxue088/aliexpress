# -*- coding: utf-8 -*-
import logging
import urlparse

from pybloom import ScalableBloomFilter
from scrapy_redis.spiders import RedisSpider

from items import UrlItem, ProductItem


class ProductSpider(RedisSpider):
    name = "product"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    prefix = ''

    def __init__(self):
        self.products = dict()
        self.urls = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)

    def start_requests(self):
        ProductSpider.prefix = self.settings['prefix']
        self.redis_key = '{}:product'.format(ProductSpider.prefix)

        for value in self.server.lrange('{}:processed'.format(ProductSpider.prefix), 0, 100000):
            self.urls.add(value)

        while True:
            request = self.next_request()
            if request:
                yield request
                break

    def make_requests_from_url(self, url):
        if not self.urls.add(url):
            return super(ProductSpider, self).make_requests_from_url(url)

    def parse(self, response):
        self.log('product url: {}'.format(response.url), logging.INFO)

        try:
            store_url = response.css('.shop-name').xpath('a/@href').extract()[0]
            self.log('crawl store url: {}'.format(store_url), logging.INFO)

            store_item = UrlItem()
            store_item['prefix'] = ProductSpider.prefix
            store_item['type'] = 'processed'
            store_item['url'] = response.url
            yield store_item

            store_item = UrlItem()
            store_item['prefix'] = ProductSpider.prefix
            store_item['type'] = 'store'
            store_item['url'] = store_url
            yield store_item

            feedback_base_url = response.xpath('//div[@id="feedback"]/iframe/@thesrc').extract()[0]
            parsed = urlparse.urlparse(feedback_base_url)
            product_id = urlparse.parse_qs(parsed.query)['productId'][0]

            try:
                percent_num = response.css('.percent-num').xpath('text()').extract()[0]
                rantings_text = response.css('.rantings-num').xpath('text()').extract()[0]
                rantings_num = rantings_text[1:rantings_text.index(' ')]
                order_text = response.css('.order-num').xpath('text()').extract()[0]
                order_num = order_text[:order_text.index(' ')]
            except:
                percent_num = 0
                rantings_num = 0
                order_num = 0

            product_item = ProductItem()
            product_item['prefix'] = ProductSpider.prefix
            product_item['_id'] = product_id
            product_item['store'] = store_url
            product_item['url'] = response.url
            product_item['percent_num'] = percent_num
            product_item['rantings_num'] = rantings_num
            product_item['order_num'] = order_num
            yield product_item

            feedback_item = UrlItem()
            feedback_item['prefix'] = ProductSpider.prefix
            feedback_item['type'] = 'feedback'
            feedback_item['url'] = feedback_base_url
            yield feedback_item

            order_item = UrlItem()
            order_item['prefix'] = ProductSpider.prefix
            order_item['type'] = 'order'
            order_item[
                'url'] = 'http://feedback.aliexpress.com/display/evaluationProductDetailAjaxService.htm?productId={}&type=default'.format(
                product_id)
            yield order_item
        except:
            try:
                product_url = response.meta['redirect_urls'][0]
            except:
                product_url = response.url
                self.log('strange product url: {}'.format(product_url), logging.ERROR)
            finally:
                self.log('meet anti-spider, back product: {}'.format(product_url), logging.INFO)

                url_item = UrlItem()
                url_item['prefix'] = ProductSpider.prefix
                url_item['type'] = 'product'
                url_item['url'] = product_url
                yield url_item
