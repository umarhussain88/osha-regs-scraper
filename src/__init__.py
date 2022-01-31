import pandas as pd 


#create logkey

def logkey() -> str:
    return 'osha_crawler_' +pd.Timestamp('now').strftime('%Y%m%d%H%M')