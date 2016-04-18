# -*- coding: utf-8 -*-
import logging
import urlparse

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

    def start_requests(self):
        ProductSpider.prefix = self.settings['prefix']
        self.redis_key = '{}:product'.format(ProductSpider.prefix)

        yield self.next_request()

    def parse(self, response):
        self.log('product url: {}'.format(response.url), logging.INFO)

        try:
            store_url = response.css('.shop-name').xpath('a/@href').extract()[0]
            self.log('crawl store url: {}'.format(store_url), logging.INFO)

            item = UrlItem()
            item['prefix'] = ProductSpider.prefix
            item['type'] = 'store'
            item['url'] = store_url
            yield item

            feedback_base_url = response.xpath('//div[@id="feedback"]/iframe/@thesrc').extract()[0]
            parsed = urlparse.urlparse(feedback_base_url)
            product_id = urlparse.parse_qs(parsed.query)['productId'][0]

            item = ProductItem()
            item['prefix'] = ProductSpider.prefix
            item['_id'] = product_id
            item['store'] = store_url
            item['url'] = response.url
            yield item

            item = UrlItem()
            item['prefix'] = ProductSpider.prefix
            item['type'] = 'feedback'
            item['url'] = feedback_base_url
            yield item

            item = UrlItem()
            item['prefix'] = ProductSpider.prefix
            item['type'] = 'order'
            item['url'] = 'http://feedback.aliexpress.com/display/evaluationProductDetailAjaxService.htm?productId={}&type=default'.format(
                product_id)
            yield item
        except:
            try:
                product_url = response.meta['redirect_urls'][0]
            except:
                product_url = response.url
                self.log('strange product url: {}'.format(product_url), logging.ERROR)
            finally:
                self.log('meet anti-spider, back product: {}'.format(product_url), logging.INFO)

                item = UrlItem()
                item['prefix'] = ProductSpider.prefix
                item['type'] = 'product'
                item['url'] = product_url
                yield item
