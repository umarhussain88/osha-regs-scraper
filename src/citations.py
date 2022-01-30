import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from src.logger import logger_util


logger = logger_util(__name__)

# get newest file in dir.
def get_newest_file(path: str):

    p = Path(__file__).parent.parent.joinpath(path)
    if not p.is_dir():
        logger.error(f"{p} is not a directory")
        raise Exception("Path is not a directory")
    files = p.glob("*.json")
    
    return max(files, key=lambda x: x.stat().st_ctime)


# flatten json file
def flatten_json(file: Path):

    df = pd.read_json(file)
    articles = df["article"].apply(lambda x: BeautifulSoup(x, "html.parser"))
    df["ExternalId"] = articles.apply(
        lambda x: x.find("article").get("data-history-node-id")
    )

    df = df.rename(columns={"article": "content"})
    return df


# create iso folder
def create_iso_folder(path: str):

    iso_date = pd.Timestamp("today").strftime("%Y-%m-%d")
    p = Path(__file__).parent.parent.joinpath(path, iso_date)
    if not p.exists():
        p.mkdir()
    logger.info(f"Created iso folder - {p}")

    return p


# strip title column
def strip_title(df: pd.DataFrame):

    df1 = df.copy()
    df1["title"] = df1["title"].str.split("-", expand=True)[0]

    return df1


# create citation dataframe
def citation_df(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Explodes along the title column after splitting out citations.
    joins and uses externalId for many:1 join"""

    citation_df = (
        dataframe[["ExternalId"]]
        .join(
            dataframe["title"]
            .str.split("- \[", expand=True)[1]
            .str.replace("\[|\]", "", regex=True)
            .str.split(";")
            .explode()
        )
        .reset_index(drop=True)
    )

    return citation_df.rename(columns={1: "Content"})
