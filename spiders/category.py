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
        return scrapy.Request(url=url, meta={'page': page})

    def parse(self, response):
        links = response.css('a.product').xpath('@href').extract()

        self.log('request page: {}, crawl product: {}'.format(response.url, len(links)), logging.INFO)

        for link in links:
            item = UrlItem()
            item['prefix'] = CategorySpider.prefix
            item['type'] = 'product'
            item['url'] = link[:link.index('?')]
            yield item

        if len(links) > 0:
            yield self.request_page(int(response.meta['page']) + 1)
        else:
            self.log('category spider finish, base url: {}'.format(self.base_url), logging.INFO)
