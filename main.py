from pathlib import Path
from sys import argv
import os 
import json
from time import sleep

import pandas as pd

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from osha.spiders import oshaSpider, StandardRegsSpider


from src import logkey
from src.citations import (citation_df, create_iso_folder, flatten_json,
                           get_newest_file, strip_title)
from src.engine import Engine
from src.logger import logger_util
from src.standards import standards_dataframe


logger = logger_util(__name__)


eng = Engine(username=os.getenv('osha_db_user'), password=os.getenv('osha_db_password'),
                                server=os.getenv('db_server'), database=os.getenv('db_name')
    )
audit_eng = Engine(username=os.getenv('osha_db_user'), password=os.getenv('osha_db_password'),
                                server=os.getenv('db_server'), database='mc_staging'
                )

if __name__ == '__main__':

    logger.info('starting articles/citations spider')


    key = eng.insert_batch_job(batch_type='articles',destination_output='output/articles.json', target_file_name='articles.json',
                               src='https://www.osha.gov/laws-regs/standardinterpretations/publicationdate')

    process = CrawlerProcess(get_project_settings())

    process.crawl(oshaSpider)
    process.start()
    row_count = pd.read_json('output/articles.json').shape[0]
    eng.update_batch_job(bid=key, row_count=row_count)

    with open('output/articles.json') as f:
        data = json.load(f)
    
    audit_df = pd.DataFrame({'batchKey' : key, 'jsonBody' : [json.dumps(data)]})
    audit_df.to_sql('oshaLOIjson',schema='stg2',con=audit_eng.engine, if_exists='append', index=False)


    key = eng.insert_batch_job(batch_type='standards',destination_output='output/standards.json',
                               src='https://www.osha.gov/laws-regs/standardinterpretations/standards', target_file_name='standards.json')
    sleep(5)
    process.crawl(StandardRegsSpider)
    process.start()                               

    row_count = pd.read_json('output/standards.json').shape[0]
    eng.update_batch_job(bid=key, row_count=row_count)

    with open('output/standards.json') as f:
        data = json.load(f)
    
    audit_df = pd.DataFrame({'batchKey' : key, 'jsonBody' : [json.dumps(data)]})
    audit_df.to_sql('oshaLOIjson',schema='stg2',con=audit_eng.engine, if_exists='append', index=False)
    



    key = eng.insert_batch_job(batch_type='main.py',destination_output='output/loi.csv',
        src='osha-regs', target_file_name='loi.csv')
                         
    logger.info(f'key is {key}')
    
    destination_path = argv[1]
    if not Path(destination_path).exists():
        logger.critical(f'{destination_path} does not exist!')
        raise Exception(f"{destination_path} does not exist!")

    logger.info(f'Destination path - {destination_path}')

    logger.info('starting program')
    file = Path(__file__).parent.joinpath('output/articles.json')   

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

    standards_file =  Path(__file__).parent.joinpath('output/standards.json')

    logger.info(f"Latest file - {standards_file.stem}")
    standards_df = standards_dataframe(standards_file)
    standards_df['Process'] = key
    standards_df.to_csv(Path(destination_path).joinpath('LoiDocuments.csv'), index=False)
    logger.info('Standards written to stg folder')
    #eng.update_batch_job(bid=key, row_count='0')
