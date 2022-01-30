from src.logger import logger_util
from src.citations import flatten_json, citation_df, create_iso_folder, strip_title, get_newest_file
import sys


logger = logger_util(__name__)


if __name__ == '__main__':
    logger.info('starting program')
    file = get_newest_file('osha/output')

    logger.info(f"Latest file - {file.stem}")
    df = flatten_json(file)
    iso_path = create_iso_folder('osha/output')

    loi = strip_title(df)
    loi.to_csv(iso_path.joinpath('letters_of_interpretation.csv'), index=False)
    logger.info('LOI written to iso folder')

    c_df = citation_df(df)
    c_df.to_csv(iso_path.joinpath('citations.csv'), index=False)
    logger.info('Citations written to iso folder')

    
