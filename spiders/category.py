# # -*- coding: utf-8 -*-
# import logging
#
# import scrapy
#
#
# class CategorySpider(scrapy.Spider):
#     name = "category"
#     allowed_domains = ["aliexpress.com"]
#     start_urls = (
#         'http://www.aliexpress.com/',
#     )
#
#     def __init__(self, baseurl):
#         self.baseurl = baseurl
#
#     def start_requests(self):
#         return self.request_page()
#
#     def request_page(self, page=1):
#         yield scrapy.Request(url='{}/{}.html'.format(self.baseurl, page), meta={'page': page})
#
#     def parse(self, response):
#         links = response.css('a.product').xpath('@href').extract()
#
#         self.log('request page: {}, crawl product: {}'.format(response.url, len(links)), logging.INFO)
#
#         with open('links.txt', 'a') as file:
#             for link in links:
#                 link = link[:link.index('?')]
#                 print link
#                 file.write('{}{}'.format(link, '\n'))
#
#         if len(links) > 0:
#             return self.request_page(int(response.meta['page']) + 1)
#         else:
#             self.log('finish')
