import scrapy

class OshaItem(scrapy.Item):
    # define the fields for your item here like:
    year = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    href = scrapy.Field()
    article = scrapy.Field()
    article_title = scrapy.Field()
    standard_title = scrapy.Field()
    standard_contents_page_title = scrapy.Field()
    standard_contents_page_content = scrapy.Field()
    standard_content = scrapy.Field()
    standard_page_title = scrapy.Field()
