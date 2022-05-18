# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PhmsaItem(scrapy.Item):
    
    page = scrapy.Field()
    section = scrapy.Field()
    subject = scrapy.Field()
    
    ref_id = scrapy.Field()
    date = scrapy.Field()
    company_name = scrapy.Field()
    individual_name = scrapy.Field()
    response_doc_href = scrapy.Field()
    
    regulation_title = scrapy.Field()
    location_state = scrapy.Field()
    country = scrapy.Field()
    response_text = scrapy.Field()
    # these are nested so leaving them out.
    # regulation_section = scrapy.Field()
    # regulation_subject = scrapy.Field()
    # regulation_href = scrapy.Field()
    
    
    
    