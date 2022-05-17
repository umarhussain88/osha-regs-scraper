from src import Exporter, logger_util, run_spider
import os 
from sys import argv
from pathlib import Path
import json
import pandas as pd


exp = Exporter(blob_storage_url=os.environ.get('BLOB_STORAGE_URL'), 
               blob_container_name=os.environ.get('BLOB_CONTAINER_NAME') )


logger = logger_util(__name__)


if __name__ == '__main__':
    
    # if len(argv) != 2:
    #     print("Usage: python main.py <spider_name> or export-azure")
    #     logger.error("No spider name provided")
    #     exit(1)
    
    argv.append('export-azure')
    
    if argv[1] == 'export-azure':
        logger.info("Exporting data to Azure Blob Storage")
        for file in Path(__file__).parent.joinpath('output').glob('*.json'):
            with open(file, 'r') as f:
                logger.info(f'Parsing {file.name}')
                j = json.load(f)
                df = pd.json_normalize(j)
                exp.write_to_blob_storage(file.stem + '.csv', df)
    else:
        spider_name = argv[1]
        run_spider(argv[1])
    
    
    