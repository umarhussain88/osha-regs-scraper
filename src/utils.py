import logging
from pathlib import Path


def logger_util(name : str) -> logging.Logger:
    logger = logging.getLogger(name)
    
    #create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    
    #create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s - %(lineno)d')
    
    #create file handler 
    if not Path(__file__).parent.parent.joinpath('logs').exists():
        Path(__file__).parent.parent.joinpath('logs').mkdir(parents=True)  
    #create file handler and set level to warning
    fh = logging.FileHandler('logs/app.log', mode='w')
    
    fh.setLevel(logging.INFO)
    
    
    #add formatter to ch
    ch.setFormatter(formatter)

    #add ch to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
