import scrapy

from ..items import OshaItem


class oshaSpider(scrapy.Spider):
    # define the fields for your item here like:
    name = "regs"
    allowed_domains = ["www.osha.gov"]
    start_urls = [
        "https://www.osha.gov/laws-regs/standardinterpretations/publicationdate"
    ]
    source_url = start_urls[0].split("/law")[0]

    # name = scrapy.Field()

    # start requests
    def parse(self, response):

        years = response.xpath(
            "//a[starts-with(@href, '/laws-regs/standardinterpretations/publicationdate/')]/@href"
        ).extract()

        for year in years:
            yield scrapy.Request(self.source_url + year, callback=self.get_pages)

    def get_pages(self, response):

        data_points = response.xpath('//div[@class="item-list"]')

        for data_point in data_points:
            items = OshaItem()
            items["year"] = response.url.split("/")[-1]
            items["date"] = data_point.xpath("ul/li/div/span/strong/text()").get()
            items["title"] = data_point.xpath("ul/li/div/span/a/text()").get()
            items["href"] = data_point.xpath("ul/li/div/span/a/@href").get()

            yield scrapy.Request(
                self.source_url + items["href"],
                callback=self.get_letters,
                meta={"items": items},
            )

    def get_letters(self, response):

        items = response.meta["items"]
        items["article"] = response.xpath("//article").get()
        yield items
