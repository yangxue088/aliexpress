# -*- coding: utf-8 -*-
import logging
from datetime import datetime

import scrapy
from scrapy_redis.spiders import RedisSpider

from items import StoreItem


class StoreSpider(RedisSpider):
    name = "store"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    prefix = ''

    def start_requests(self):
        StoreSpider.prefix = self.settings['prefix']
        self.redis_key = '{}:store'.format(StoreSpider.prefix)

        yield self.next_request()

    def parse(self, response):
        self.log('request store: {}'.format(response.url), logging.INFO)

        owner_member_id = response.css('.s-alitalk').xpath('a/@data-id1').extract()[0]
        evaluation_detail_url = 'http://feedback.aliexpress.com/display/evaluationDetail.htm?ownerMemberId={}'.format(owner_member_id)
        return scrapy.Request(url=evaluation_detail_url, callback=self.parse_evaluation_detail)

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

        store_id = store_url[store_url.index('/') + 1:]

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

        product_num = int(response.xpath('//div[@id="result-info"]/strong/text()').extract()[0])
        item['product'] = product_num

        return item
