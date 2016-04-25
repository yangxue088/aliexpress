# -*- coding: utf-8 -*-
import logging
from datetime import datetime

import scrapy
from pybloom import ScalableBloomFilter
from pymongo import MongoClient
from scrapy_redis.spiders import RedisSpider

from items import StoreItem, UrlItem


class StoreSpider(RedisSpider):
    name = "store"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    prefix = ''

    stores = ScalableBloomFilter(mode=ScalableBloomFilter.LARGE_SET_GROWTH)

    def start_requests(self):
        StoreSpider.prefix = self.settings['prefix']
        self.redis_key = '{}:store'.format(StoreSpider.prefix)

        db = MongoClient().aliexpress
        for store in db['{}store'.format(StoreSpider.prefix)].find():
            StoreSpider.stores.add(store['url'])

        yield self.next_request()

    def make_requests_from_url(self, url):
        if not StoreSpider.stores.add(url):
            return super(StoreSpider, self).make_requests_from_url(url)
        else:
            return self.next_request()

    def parse(self, response):
        try:
            self.log('request store: {}'.format(response.url), logging.INFO)

            owner_member_id = response.css('.s-alitalk').xpath('a/@data-id1').extract()[0]
            evaluation_detail_url = 'http://feedback.aliexpress.com/display/evaluationDetail.htm?ownerMemberId={}'.format(owner_member_id)
            yield scrapy.Request(url=evaluation_detail_url, callback=self.parse_evaluation_detail)
        except:
            try:
                store_url = response.meta['redirect_urls'][0]
            except:
                store_url = response.url
                self.log('strange store url: {}'.format(store_url), logging.ERROR)
            finally:
                self.log('meet anti-spider, back store: {}'.format(store_url), logging.INFO)

                url_item = UrlItem()
                url_item['prefix'] = StoreSpider.prefix
                url_item['type'] = 'store'
                url_item['url'] = store_url
                yield url_item

    def parse_evaluation_detail(self, response):
        summary_tb_tds = response.xpath('//div[@id="feedback-summary"]/div/table/tbody/tr/td')
        store_name = summary_tb_tds[0].xpath('a/text()').extract()[0]
        store_url = summary_tb_tds[0].xpath('a/@href').extract()[0]
        store_positive_feedback = summary_tb_tds[1].xpath('span/text()').extract()[0]
        store_positive_score = int(summary_tb_tds[2].xpath('span/text()').extract()[0].replace(',', ''))
        store_since_time = datetime.strptime(summary_tb_tds[3].xpath('text()').extract()[0].strip(), '%d %b %Y')

        history_tds = response.xpath('//div[@id="feedback-history"]/div/table/tbody/tr/td/a/text()').extract()
        one_month_feedback = [int(td.strip().replace(',', '').replace('-', '0')) for td in history_tds[::5]]
        three_month_feedback = [int(td.strip().replace(',', '').replace('-', '0')) for td in history_tds[1::5]]
        six_month_feedback = [int(td.strip().replace(',', '').replace('-', '0')) for td in history_tds[2::5]]
        twelve_month_feedback = [int(td.strip().replace(',', '').replace('-', '0')) for td in history_tds[3::5]]
        overall_feedback = [int(td.strip().replace(',', '').replace('-', '0')) for td in history_tds[4::5]]

        store_id = store_url.split('/')[-1]

        if not self.stores.add(store_id):
            item = StoreItem()
            item['prefix'] = StoreSpider.prefix
            item['_id'] = store_id
            item['url'] = store_url
            item['name'] = store_name
            item['positive_feedback'] = store_positive_feedback
            item['positive_score'] = store_positive_score
            item['since_time'] = store_since_time
            item['one_month_feedback'] = one_month_feedback
            item['three_month_feedback'] = three_month_feedback
            item['six_month_feedback'] = six_month_feedback
            item['twelve_month_feedback'] = twelve_month_feedback
            item['overall_feedback'] = overall_feedback

            all_product_url = 'http://www.aliexpress.com/store/all-wholesale-products/{}.html'.format(store_id)
            return scrapy.Request(all_product_url, meta={'item': item}, callback=self.parse_product_num)

    def parse_product_num(self, response):
        item = response.meta['item']

        product_num = int(response.xpath('//div[@id="result-info"]/strong/text()').extract()[0].replace(',', ''))
        item['product'] = product_num

        return item
