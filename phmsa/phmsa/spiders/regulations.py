import scrapy
from ..items import PhmsaItem
from typing import Optional



class RegulationsSpider(scrapy.Spider):
    name = 'regulations'
    allowed_domains = ['www7.phmsa.dot.gov', 'www.phmsa.dot.gov']

    start_urls = [
        'https://www7.phmsa.dot.gov/regulations/title49/b/2/1/list?']

    custom_settings: Optional[dict] = {
        "FEEDS": {
            "output/phmsa_regulations.json": {
                "format": "json",
                "overwrite": True
            }

        }
    }


    #TO DO 
    #ensure I follow pages vertically and get all the data.
    # currently I'm skipping sections and just getting the first page of data.
    
    #pathway should be 
    #regulations
    #subjects
    #subject pages
    #regulations pages details
    
    source_url = start_urls[0].split('/regulations')[0]
    
    def parse(self,response):
        
        
        
        page_url = response.xpath('//li[@class="pager-last last"]/a/@href').get().split('=')
        pages = page_url[-1]
        
        for page in range(0, int(pages) + 1):
            
            items = PhmsaItem()
            items['page'] = f"{page_url[0]}={page}" 
            yield scrapy.Request(self.source_url + f"{page_url[0]}={page}" , callback=self.get_subjects, meta={'items': items})
        
    
    def get_subjects(self, response):
        
        subjects = response.xpath('//table[@class="dot-table dot-regulations-table tablesaw tablesaw-stack"]/tbody/tr')
        
        for subject in subjects:
            items = response.meta['items']
            items['section'] = subject.xpath('td/text()')[0].get().strip()
            items['subject'] = subject.xpath('td/a/text()').get().strip()
            
            url = subject.xpath('td/a/@href').get()
            yield scrapy.Request(self.source_url + url, callback=self.get_regulation_list,
                                 meta={'items': items})
    
    def get_regulation_list(self, response):
        
        
        table = response.xpath('//table[@class="dot-table dot-regulations-table tablesaw tablesaw-stack"]/tbody/tr')
        
        for row in table:
            
            items = response.meta['items']
            row_body = row.xpath('td')
            follow = row.xpath('td')[0].xpath('a/@href').get()
            items['ref_id'] = follow.split('/')[-1]
            items['date'] = row_body[1].xpath('text()').get().strip()
            items['company_name'] = row_body[2].xpath('text()').get().strip()
            items['individual_name'] = row_body[3].xpath('text()').get().strip()
            items['response_doc_href'] = row_body[4].xpath('a/@href').get()
            
            
            yield scrapy.Request(self.source_url + follow, callback=self.get_regulation_detail,
                                 meta={'items': items})
            
    def get_regulation_detail(self, response):
        
        items = response.meta['items']
        items['regulation_title'] = response.xpath('//h1[@class="title"]/text()').get().strip()
        items['location_state'] =  response.xpath('//b[contains(.,"Location state:")]').xpath('./following-sibling::node()[1]').get().strip()
        items['country'] =  response.xpath('//b[contains(.,"Country:")]').xpath('./following-sibling::node()[1]').get().strip()
        items['response_text'] =  response.xpath('//section[@id="content-wall"]').get()
        yield items

        
        
        
        
            
        
        
    
    
