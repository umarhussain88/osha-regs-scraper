import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from src.logger import logger_util


logger = logger_util(__name__)



def standards_dataframe(path : str ) -> pd.DataFrame:

    if not Path(path).exists():
        logger.error(f'file path does not exists {path}')
        raise FileNotFoundError(f"{path} does not exist")

    standard_df = pd.read_json(path)

    standard_df['Name'] = standard_df["standard_title"].str.extract("Part (\d+) -")

    standard_df['Content'] = standard_df["standard_page_title"] + '\n' + standard_df["standard_content"]

    final_df = standard_df[['Name', 'Content']]

    return final_df




    