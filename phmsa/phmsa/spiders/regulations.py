import scrapy
from ..items import PhmsaItem
from typing import Optional

import logging
from scrapy.shell import inspect_response


class RegulationsSpider(scrapy.Spider):
    name = 'regulations'
    allowed_domains = ['www7.phmsa.dot.gov', 'www.phmsa.dot.gov']

    start_urls = [
        'https://www7.phmsa.dot.gov/regulations/title49/b/2/1/list?']

    custom_settings: Optional[dict] = {
        "FEEDS": {
            "output/phmsa_regulations.json": {
                "format": "json",
                "overwrite": True,
                "logging_level" : "ERROR"
            }

        }
    }

    source_url = start_urls[0].split('/regulations')[0]

    def parse(self, response):

        page_url = response.xpath(
            '//li[@class="pager-last last"]/a/@href').get().split('=')
        pages = page_url[-1]

        for page in range(0, int(pages) + 1):

            url = self.source_url + f"{page_url[0]}={page}"
            self.log(url, logging.WARN)
            yield scrapy.Request(url, callback=self.get_subjects, meta={'page': f"{page_url[0]}={page}"})

    def get_subjects(self, response):

        subjects = response.xpath(
            '//table[@class="dot-table dot-regulations-table tablesaw tablesaw-stack"]/tbody/tr')

        for each_subject in subjects:

            section = each_subject.xpath('td/text()')[0].get().strip()
            subject = each_subject.xpath('td/a/text()').get().strip()

            url = each_subject.xpath('td/a/@href').get()
            self.log(url, logging.WARN)
            yield scrapy.Request(self.source_url + url, callback=self.get_regulation_list_pages,
                                 meta={'subject': subject, 'section': section, 'page': response.meta['page']})

    def get_regulation_list_pages(self, response):

        page_url = response.xpath('//a[@title="Go to last page"]/@href').get()

        if page_url:
            page_url = page_url.split('=')
            last_page = page_url[-1]

            for page in range(0, int(last_page) + 1):
                follow_page = f"{page_url[0]}={page}"
                self.log(follow_page, logging.WARN)

                yield scrapy.Request(self.source_url + follow_page, callback=self.get_regulation_list,
                                     meta={'subject': response.meta['subject'],
                                           'section': response.meta['section'],
                                           'page': response.meta['page'],
                                           'regulation_list_page': follow_page})

        else:
            url = response.url.split('.gov')[1]
            self.log(self.source_url + url, logging.WARN)
            yield scrapy.Request(self.source_url + url, dont_filter=True,
                                 callback=self.get_regulation_list, meta={'subject': response.meta['subject'],
                                                                          'section': response.meta['section'],
                                                                          'page': response.meta['page']})

    def get_regulation_list(self, response):

        table = response.xpath(
            '//table[@class="dot-table dot-regulations-table tablesaw tablesaw-stack"]/tbody/tr')

        for row in table:

            items = PhmsaItem()

            items['page'] = response.meta['page']
            items['section'] = response.meta['section']
            items['subject'] = response.meta['subject']

            if response.meta.get('regulation_list_page'):
                items['regulation_list_page'] = response.meta['regulation_list_page']

            row_body = row.xpath('td')
            follow = row.xpath('td')[0].xpath('a/@href').get()
            items['ref_id'] = follow.split('/')[-1]
            items['date'] = row_body[1].xpath('text()').get().strip()
            items['company_name'] = row_body[2].xpath('text()').get().strip()
            items['individual_name'] = row_body[3].xpath(
                'text()').get().strip()
            items['response_doc_href'] = row_body[4].xpath('a/@href').get()

            self.log(follow, logging.WARN)
            yield scrapy.Request(self.source_url + follow, callback=self.get_regulation_detail,
                                 meta={'items': items})

    def get_regulation_detail(self, response):

        items = response.meta['items']
        items['regulation_title'] = response.xpath(
            '//h1[@class="title"]/text()').get().strip()
        state = response.xpath(
            '//b[contains(.,"Location state:")]').xpath('./following-sibling::node()[1]').get()
        if state:
            items['location_state'] = state.strip()
        country = response.xpath(
            '//b[contains(.,"Country:")]').xpath('./following-sibling::node()[1]').get()
        if country:
            items['country'] = country.strip()
        items['response_text'] = response.xpath(
            '//section[@id="content-wall"]').get()
        yield items
