# -*- coding: utf-8 -*-
import scrapy


class ProductSpider(scrapy.Spider):
    name = "product"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    def __init__(self, url):
        self.url = url

    def start_requests(self):
        yield self.make_requests_from_url(self.url)

    def parse(self, response):


