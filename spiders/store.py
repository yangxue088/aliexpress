# -*- coding: utf-8 -*-
import scrapy


class StoreSpider(scrapy.Spider):
    name = "store"
    allowed_domains = ["aliexpress.com"]
    start_urls = (
        'http://www.aliexpress.com/',
    )

    def __init__(self, url):
        self.url = url

    def start_requests(self):
        yield self.make_requests_from_url(self.url)

    def parse(self, response):
        owner_member_id = response.css('.s-alitalk').xpath('a/@data-id1').extract()[0]
        evaluation_detail_url = 'http://feedback.aliexpress.com/display/evaluationDetail.htm?ownerMemberId={}'.format(owner_member_id)
        return scrapy.Request(url=evaluation_detail_url, callback=self.parse_evaluation_detail)

    def parse_evaluation_detail(self, response):
        summary_tb_tds = response.xpath('//div[@id="feedback-summary"]/div/table/tbody/tr/td')
        store_name = summary_tb_tds[0].xpath('a/text()').extract()[0]
        store_url = summary_tb_tds[0].xpath('a/@href').extract()[0]
        store_positive_feedback = summary_tb_tds[1].xpath('span/text()').extract()[0]
        store_positive_score= summary_tb_tds[2].xpath('span/text()').extract()[0]
        store_since_time = summary_tb_tds[3].xpath('text()').extract()[0].strip()

        history_tds = response.xpath('//div[@id="feedback-history"]/div/table/tbody/tr/td/a/text()').extract()
        1_month_feedback = [int(td.strip().replace(',', '')) for td in history_tds[::5]]
        3_month_feedback = [int(td.strip().replace(',', '')) for td in history_tds[1::5]]
        6_month_feedback = [int(td.strip().replace(',', '')) for td in history_tds[2::5]]
        12_month_feedback = [int(td.strip().replace(',', '')) for td in history_tds[3::5]]
        overall_feedback = [int(td.strip().replace(',', '')) for td in history_tds[4::5]]

