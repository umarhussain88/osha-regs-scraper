from bs4 import BeautifulSoup
import pandas as pd 
from pathlib import Path 
from bs4 import BeautifulSoup




#get newest file in dir.
def get_newest_file(path : str):
    p = Path(__file__).parent.joinpath(path)
    if not p.is_dir():
        raise Exception("Path is not a directory")        
    files = p.glob('*.json')
    return max(files, key=lambda x: x.stat().st_ctime)


#flatten json file
def flatten_json(file : Path):

    df = pd.read_json(file)
    articles = df['article'].apply(lambda x : BeautifulSoup(x, 'html.parser'))
    df['ExternalId'] = articles.apply(lambda x : x.find('article').get("data-history-node-id"))
    return df

#create iso folder
def create_iso_folder(path : str):
    iso_date = pd.Timestamp('today').strftime('%Y-%m-%d')
    p = Path(__file__).parent.joinpath(path,iso_date)
    if not p.exists():
        p.mkdir()
    return p



if __name__ == '__main__':

    file = get_newest_file('osha/output')
    df = flatten_json(file)
    iso_path = create_iso_folder('osha/output')
    df.to_csv(iso_path.joinpath('osha_flattened.csv'), index=False)
