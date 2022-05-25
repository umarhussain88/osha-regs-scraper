from src import Exporter, logger_util, run_spider, parse_reponse_text_html, parse_regulations
import os
from sys import argv
from pathlib import Path
import json
import pandas as pd


exp = Exporter(blob_storage_url=os.environ.get('BLOB_STORAGE_URL'),
               blob_container_name=os.environ.get('BLOB_CONTAINER_NAME'))


logger = logger_util(__name__)


if __name__ == '__main__':

    if len(argv) != 2:
        print("Usage: python main.py <spider_name> or export-azure")
        logger.error("No spider name provided")
        exit(1)

    if argv[1] == 'export-azure':
        logger.info("Exporting data to Azure Blob Storage")
        for file in Path(__file__).parent.joinpath('output').glob('*.json'):
            with open(file, 'r') as f:
                logger.info(f'Parsing {file.name}')
                j = json.load(f)
                df = pd.json_normalize(j)
                exp.write_to_blob_storage(file.stem + '.csv', df)

    elif argv[1] == 'clean-phmsa-regulations':

        with open('phmsa/output/phmsa_regulations.json') as f:
            j = json.load(f)

        df = pd.json_normalize(j)

        df['response_text_html'] = parse_reponse_text_html(df)
        df['regulations'] = parse_regulations(df)

        logger.info(
            f'Writing {df.shape[0]} rows to blob storage as phmsa_regulations.csv')

        exp.write_to_blob_storage('phmsa_regulations.csv', df)

    else:
        spider_name = argv[1]
        run_spider(argv[1])
