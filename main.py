from pathlib import Path
from sys import argv

import pandas as pd

from scrapy.crawler import CrawlerProcess
from osha.spiders import oshaSpider, StandardRegsSpider


from src import logkey
from src.citations import (citation_df, create_iso_folder, flatten_json,
                           get_newest_file, strip_title)
from src.engine import Engine
from src.logger import logger_util
from src.standards import standards_dataframe


logger = logger_util(__name__)

eng = Engine()

if __name__ == '__main__':

    logger.info('starting articles/citations spider')


    key = eng.insert_batch_job(batch_type='articles',destination_output='output/articles.json',
                               src='https://www.osha.gov/laws-regs/standardinterpretations/publicationdate')

    
    #start process crawler and output to json

    process = CrawlerProcess({'FEED_FORMAT': 'json','FEED_URI': 'output/articles.json'})
    process.crawl(oshaSpider)
    process.start()
    row_count = pd.read_json('output/standards.json').shape[0]
    eng.update_batch_job(bid=key, row_count=row_count)


    process = CrawlerProcess({'FEED_FORMAT': 'json','FEED_URI': 'output/standards.json'})
    key = eng.insert_batch_job(batch_type='articles',destination_output='output/articles.json',
                               src='https://www.osha.gov/laws-regs/standardinterpretations/standards')
    process.crawl(StandardRegsSpider)
    process.start()                               

    row_count = pd.read_json('output/standards.json').shape[0]
    eng.update_batch_job(bid=key, row_count=row_count)



    eng.insert_batch_job(batch_type='main.py - etl', destination_path='/stg1/', )
    destination_path = argv[1]
    if not Path(destination_path).exists():
        logger.critical(f'{destination_path} does not exist!')
        raise Exception(f"{destination_path} does not exist!")

    logger.info(f'Destination path - {destination_path}')

    logger.info('starting program')
    file = Path(__file__).parent.joinpath('output/articles.json')
    key = logkey()
    logger.info(f'key is {key}')

    logger.info(f"Latest file - {file.stem}")
    df = flatten_json(file)

    loi = strip_title(df)
    loi['Process'] = key
    loi.to_csv(Path(destination_path).joinpath('letters_of_interpretation.csv'), index=False)
    

    logger.info('LOI written to stg folder')

    c_df = citation_df(df)
    c_df['Process'] = key
    c_df.to_csv(Path(destination_path).joinpath('citations.csv'), index=False)
    logger.info('Citations written to stg folder')

    standards_file =  Path(__file__).joinpath('output/standards.json')

    logger.info(f"Latest file - {standards_file.stem}")
    standards_df = standards_dataframe(standards_file)
    standards_df['Process'] = key
    standards_df.to_csv(Path(destination_path).joinpath('LoiDocuments.csv'), index=False)
    logger.info('Standards written to stg folder')
    eng.update_batch_job(bid=key, row_count=0)
