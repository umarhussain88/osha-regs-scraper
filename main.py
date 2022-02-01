from src.logger import logger_util
from src.citations import flatten_json, citation_df, create_iso_folder, strip_title, get_newest_file
from src import logkey
from src.standards import standards_dataframe
from src.engine import Engine
import sys
from pathlib import Path
from sys import argv

logger = logger_util(__name__)


# eng = Engine()

if __name__ == '__main__':

    destination_path = argv[1]
    if not Path(destination_path).exists():
        logger.critical(f'{destination_path} does not exist!')
        raise Exception(f"{destination_path} does not exist!")

    logger.info(f'Destination path - {destination_path}')

    logger.info('starting program')
    file = Path(__file__).parent.joinpath('osha/output/articles.json')
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

    standards_file =  Path(destination_path).joinpath('standards.json')

    logger.info(f"Latest file - {standards_file.stem}")
    standards_df = standards_dataframe(standards_file)
    standards_df['Process'] = key
    standards_df.to_csv(Path(destination_path).joinpath('LoiDocuments.csv'), index=False)
    logger.info('Standards written to stg folder')


    




