# -*- coding: utf-8 -*-
import logging

import scrapy

from items import UrlItem


class CategorySpider(scrapy.Spider):
    name = "category"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    prefix = ''
    base_url = ''

    def __init__(self, reducer):
        self.reducer = reducer

    def start_requests(self):
        CategorySpider.prefix = self.settings['prefix']
        CategorySpider.base_url = self.settings['base_url']
        yield self.request_page()

    def request_page(self, page=1):
        url = CategorySpider.base_url

        if '.html' in url:
            # 按类别进行搜索
            url = url[:url.index('.html')] + '/{}'.format(page) + url[url.index('.html'):]
        else:
            # 按关键词进行搜索
            url = '{}&page={}'.format(url, page)

        self.log('request url: {}'.format(url), logging.INFO)
        return scrapy.Request(url=url, meta={'page': page}, callback=self.parse)

    def parse(self, response):
        list_items = [item.css('a.product').xpath('@href').extract() + item.css('a.rate-num').xpath('text()').extract() +
                      item.css('a.order-num-a').xpath('em/text()').extract() for item in response.css('li.list-item')]

        self.log('request page: {}, crawl product: {}'.format(response.url, len(list_items)), logging.INFO)

        for href, rate, order in (
                (list_item[0][:list_item[0].index('?')], int(list_item[1][list_item[1].index('(') + 1:list_item[1].index(')')]),
                 float(list_item[2][list_item[2].index('(') + 1:list_item[2].index(')')])) for list_item in
                list_items if
                        len(list_item) == 3):
            if self.reducer(rate, order):
                item = UrlItem()
                item['prefix'] = CategorySpider.prefix
                item['type'] = 'product'
                item['url'] = href
                yield item

        if len(list_items) > 0:
            yield self.request_page(int(response.meta['page']) + 1)
        else:
            self.log('category spider finish, base url: {}'.format(self.base_url), logging.INFO)
