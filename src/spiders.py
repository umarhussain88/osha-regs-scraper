from sys import argv
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from osha.spiders import oshaSpider, StandardRegsSpider




#generic func to run spider
def run_spider(spider_name : str , settings = get_project_settings):

    spider_names = {'oshaSpider' : oshaSpider, 'StandardRegsSpider' : StandardRegsSpider}

    if spider_name not in spider_names:
        raise ValueError('spider_name not found in spider_names')
    
    spider_name = spider_names.get(spider_name)

    process = CrawlerProcess(settings())
    process.crawl(spider_name)
    process.start()


