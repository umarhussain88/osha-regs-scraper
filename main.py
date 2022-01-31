from src.logger import logger_util
from src.citations import flatten_json, citation_df, create_iso_folder, strip_title, get_newest_file
from src import logkey
from src.standards import standards_dataframe
import sys
from pathlib import Path

logger = logger_util(__name__)


if __name__ == '__main__':
    logger.info('starting program')
    file = Path(__file__).parent.joinpath('osha/output/articles.json')
    key = logkey()
    logger.info(f'key is {key}')

    logger.info(f"Latest file - {file.stem}")
    df = flatten_json(file)
    iso_path = create_iso_folder('osha/output')

    loi = strip_title(df)
    loi['Process'] = key
    loi.to_csv(iso_path.joinpath('letters_of_interpretation.csv'), index=False)
    

    logger.info('LOI written to iso folder')

    c_df = citation_df(df)
    c_df['Process'] = key
    c_df.to_csv(iso_path.joinpath('citations.csv'), index=False)
    logger.info('Citations written to iso folder')

    standards_file =  Path(__file__).parent.joinpath('osha/output/standards.json')

    logger.info(f"Latest file - {standards_file.stem}")
    standards_df = standards_dataframe(standards_file)
    standards_df['Process'] = key
    standards_df.to_csv(iso_path.joinpath('standards.csv'), index=False)
    

    
