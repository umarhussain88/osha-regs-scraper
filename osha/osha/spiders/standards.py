import scrapy
from ..items import OshaItem
from bs4 import BeautifulSoup

class StandardRegsSpider(scrapy.Spider):
    name = "standards"
    allowed_domains = ["www.osha.gov"]
    start_urls = [
        "https://www.osha.gov/laws-regs/standardinterpretations/standardnumber"
    ]

    source_url = "https://www.osha.gov"
    custom_settings = {
        "FEEDS" : {
            "output/standards.json" :{ 
            "format" : "json",
            "overwrite" : True
            }

        }
    }



    def parse(self, response):

        regs = response.xpath('//div[@class="item-list"]/ul/li')

        for reg in regs:
            items = OshaItem()

            items["standard_title"] = reg.xpath(
                "div/span/a/text()"
            ).get()  # this isn't used but might be useful later

            yield scrapy.Request(
                self.source_url + reg.xpath("div/span/a/@href").get(),
                callback=self.get_standard_content,
                meta={"items": items},
            )

    def get_standard_content(self, response):

        items = response.meta["items"]
        items["standard_page_title"] = response.xpath("//title").get()

        items["standard_content"] = response.xpath(
            '//div[@class="views-element-container form-group"]'
        ).get()
        urls = response.xpath('//div[@class="item-list"]/ul/li/div/span/a/@href')

        for url in urls:
            yield scrapy.Request(
                self.source_url + url.get(),
                callback=self.get_child_reg,
                meta={"items": items},
            )

    def get_child_reg(self, response):

        items = response.meta["items"]


        items["standard_page_title"] = response.xpath("//title").get()
        
        items["standard_content"] = response.xpath(
            '//div[@class="views-element-container form-group"]'
        ).get()
        
        yield items
