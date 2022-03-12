from sys import argv
from src.spiders import run_spider


if __name__ == '__main__':
    spider_name = argv[1]
    run_spider(spider_name)