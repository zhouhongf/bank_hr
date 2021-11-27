import os
import sys
import time
from config import CONFIG
import schedule
from myspiders import spider_console, master_console
from database.bankends import redis_database

# 将scheduled_task.py文件所在的目录的绝对路径添加到环境变量中去
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def refresh_task():
    master_interval = CONFIG.SCHEDULED_DICT['master_interval']
    print('==================================================== 执行refresh_master的schedule, 时间间隔为：', master_interval)
    schedule.every(master_interval).minutes.do(master_console)
    time.sleep(2)

    spider_interval = CONFIG.SCHEDULED_DICT['spider_interval']
    print('==================================================== 执行refresh_spider的schedule, 时间间隔为：', spider_interval)
    schedule.every(spider_interval).minutes.do(spider_console)
    time.sleep(2)

    while True:
        schedule.run_pending()
        time.sleep(10)


if __name__ == '__main__':
    # redis_database.test()
    spider_console()
    time.sleep(10)
    master_console()
    time.sleep(10)
    refresh_task()

