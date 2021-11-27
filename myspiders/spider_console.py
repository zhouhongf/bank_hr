import os
import sys
import time
from config import CONFIG
from importlib import import_module

# sys.path.append('../')

def file_name(file_dir=os.path.join(CONFIG.BASE_DIR, 'myspiders/spider_hr')):
    all_files = []
    for file in os.listdir(file_dir):
        if file.endswith('_spider.py'):
            all_files.append(file.replace('.py', ''))
    return all_files


def spider_console():
    start = time.time()

    all_files = file_name()
    for spider in all_files:
        spider_module = import_module("myspiders.spider_hr.{}".format(spider))
        spider_module.start()

    print("【spider_console】 Time costs: {0}".format(time.time() - start))


if __name__ == '__main__':
    spider_console()
