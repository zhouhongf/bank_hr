# -*- coding: utf-8 -*-
import time
from datetime import datetime, date, timedelta
from numpy import long
import locale
import re


def timestamp_to_strtime(timestamp):
    """将 13 位整数的毫秒时间戳转化成本地普通时间 (字符串格式)
    :param timestamp: 13 位整数的毫秒时间戳 (1456402864242)
    :return: 返回字符串格式 {str}'2016-02-25 20:21:04.242000'
    """
    local_str_time = datetime.fromtimestamp(timestamp / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
    return local_str_time


def timestamp_to_datetime(timestamp):
    """将 13 位整数的毫秒时间戳转化成本地普通时间 (datetime 格式)
    :param timestamp: 13 位整数的毫秒时间戳 (1456402864242)
    :return: 返回 datetime 格式 {datetime}2016-02-25 20:21:04.242000
    """
    local_dt_time = datetime.fromtimestamp(timestamp / 1000.0)
    return local_dt_time


def datetime_to_strtime(datetime_obj):
    """将 datetime 格式的时间 (含毫秒) 转为字符串格式
    :param datetime_obj: {datetime}2016-02-25 20:21:04.242000
    :return: {str}'2016-02-25 20:21:04.242'
    """
    local_str_time = datetime_obj.strftime("%Y-%m-%d %H:%M:%S.%f")
    return local_str_time


def datetime_to_timestamp(datetime_obj):
    """将本地(local) datetime 格式的时间 (含毫秒) 转为毫秒时间戳
    :param datetime_obj: {datetime}2016-02-25 20:21:04.242000
    :return: 13 位的毫秒时间戳  1456402864242
    """
    local_timestamp = long(time.mktime(datetime_obj.timetuple()) * 1000.0 + datetime_obj.microsecond / 1000.0)
    return local_timestamp


def strtime_to_datetime(timestr):
    """将字符串格式的时间 (含毫秒) 转为 datetiem 格式
    :param timestr: {str}'2016-02-25 20:21:04.242'
    :return: {datetime}2016-02-25 20:21:04.242000
    """
    local_datetime = datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")
    return local_datetime


def strtime_to_timestamp(local_timestr):
    """将本地时间 (字符串格式，含毫秒) 转为 13 位整数的毫秒时间戳
    :param local_timestr: {str}'2016-02-25 20:21:04.242'
    :return: 1456402864242
    """
    local_datetime = strtime_to_datetime(local_timestr)
    timestamp = datetime_to_timestamp(local_datetime)
    return timestamp


def current_datetime():
    """返回本地当前时间, 包含datetime 格式, 字符串格式, 时间戳格式
    :return: (datetime 格式, 字符串格式, 时间戳格式)
    """
    # 当前时间：datetime 格式
    local_datetime_now = datetime.now()
    # 当前时间：字符串格式
    local_strtime_now = datetime_to_strtime(local_datetime_now)
    # 当前时间：时间戳格式 13位整数
    local_timestamp_now = datetime_to_timestamp(local_datetime_now)
    return local_datetime_now, local_strtime_now, local_timestamp_now


def current_standard_time():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def current_timestamp():
    return int(time.time() * 1000)


def get_current_time(is_chinese=False):
    if not is_chinese:
        return time.strftime('%Y-%m-%d %H:%M:%S')
    elif is_chinese:
        locale.setlocale(locale.LC_CTYPE, 'chinese')
        return time.strftime('%Y年%m月%d日%H时%M分%S秒')


def get_week_day():
    date = datetime.now()
    week_day_dict = {
        0: '星期一',
        1: '星期二',
        2: '星期三',
        3: '星期四',
        4: '星期五',
        5: '星期六',
        6: '星期天',
    }
    day = date.weekday()
    return week_day_dict[day]


def get_week_yesterday():
    today = date.today()
    yesterday = today - timedelta(days=1)
    thistime = yesterday.isoweekday()
    a = ''
    if thistime == 1:
        a = "星期一"
    elif thistime == 2:
        a = "星期二"
    elif thistime == 3:
        a = "星期三"
    elif thistime == 4:
        a = "星期四"
    elif thistime == 5:
        a = "星期五"
    elif thistime == 6:
        a = "星期六"
    elif thistime == 7:
        a = "星期日"
    return a


def get_current_week():
    monday, sunday = date.today(), date.today()
    one_day = timedelta(days=1)
    while monday.weekday() != 0:
        monday -= one_day
    while sunday.weekday() != 6:
        sunday += one_day
    return monday, sunday


def get_last_sunday():
    monday = date.today()
    one_day = timedelta(days=1)
    while monday.weekday() != 0:
        monday -= one_day
    last_sunday = monday - one_day
    return last_sunday.strftime("%Y-%m-%d %H:%M:%S")


def get_week_number(strtime: str = None):
    if strtime:
        try:
            number = datetime.strptime(strtime, "%Y-%m-%d %H:%M:%S").strftime("%W")
        except:
            number = datetime.strptime(strtime, "%Y/%m/%d %H:%M:%S").strftime("%W")
    else:
        number = date.today().strftime("%W")
    return number

def daytime_standard(daytimestr: str):
    list_timestr = daytimestr.split(' ')
    if len(list_timestr) == 2:
        date = list_timestr[0]
        time = list_timestr[1]
        date = strdate_standard(date)
        time = strtime_standard(time)
        return date + ' ' + time
    elif len(list_timestr) == 1:
        date = list_timestr[0]
        date = strdate_standard(date)
        return date + ' 00:00:00'

def strdate_standard(datestr: str):
    list_date = []
    if '-' in datestr:
        list_date = datestr.split('-')
    elif '/' in datestr:
        list_date = datestr.split('/')
    elif '.' in datestr:
        list_date = datestr.split('.')

    if len(list_date) == 3:
        year = list_date[0]
        month = list_date[1]
        day = list_date[2]
        if len(year) == 2:
            year = '20' + year
        if len(month) == 1:
            month = '0' + month
        if len(day) == 1:
            day = '0' + day
        return year + '-' + month + '-' + day
    else:
        return ''

def strtime_standard(timestr: str):
    list_time = timestr.split(':')
    if len(list_time) == 3:
        hour = list_time[0]
        minute = list_time[1]
        second = list_time[2]
        if len(hour) == 1:
            hour = '0' + hour
        if len(minute) == 1:
            minute = '0' + minute
        if len(second) == 1:
            second = '0' + second
        return hour + ':' + minute + ':' + second
    elif len(list_time) == 2:
        hour = list_time[0]
        minute = list_time[1]
        if len(hour) == 1:
            hour = '0' + hour
        if len(minute) == 1:
            minute = '0' + minute
        return hour + ':' + minute + ':00'
    elif len(list_time) == 1:
        hour = list_time[0]
        if len(hour) == 1:
            hour = '0' + hour
        return hour + ':00:00'
    else:
        return ''


def chinese_to_number(value: str):
    if value == '十':
        return 10
    pattern = re.compile(r'[一二三四五六七八九十]+')
    pattern_ten_one = re.compile(r'[1-9]+十[1-9]+')
    pattern_ten_two = re.compile(r'[1-9]十')
    pattern_ten_three = re.compile(r'十[1-9]')
    res = pattern.search(value)
    if not res:
        return 0
    dig = res.group()
    if '一' in dig:
        dig = dig.replace('一', '1')
    if '二' in dig:
        dig = dig.replace('二', '2')
    if '三' in dig:
        dig = dig.replace('三', '3')
    if '四' in dig:
        dig = dig.replace('四', '4')
    if '五' in dig:
        dig = dig.replace('五', '5')
    if '六' in dig:
        dig = dig.replace('六', '6')
    if '七' in dig:
        dig = dig.replace('七', '7')
    if '八' in dig:
        dig = dig.replace('八', '8')
    if '九' in dig:
        dig = dig.replace('九', '9')
    if '十' not in dig:
        return int(dig)
    res_ten_one = pattern_ten_one.fullmatch(dig)
    if res_ten_one:
        dig = dig.replace('十', '')
        return int(dig)
    res_ten_two = pattern_ten_two.fullmatch(dig)
    if res_ten_two:
        dig = dig.replace('十', '0')
        return int(dig)
    res_ten_three = pattern_ten_three.fullmatch(dig)
    if res_ten_three:
        dig = dig.replace('十', '1')
        return int(dig)
    return 0


if __name__ == '__main__':
    time_str = '2016-02-25 20:21:04.242'
    timestamp1 = strtime_to_timestamp(time_str)
    datetime1 = strtime_to_datetime(time_str)
    time_str2 = datetime_to_strtime(datetime1)
    timestamp2 = datetime_to_timestamp(datetime1)
    datetime3 = timestamp_to_datetime(timestamp2)
    time_str3 = timestamp_to_strtime(timestamp2)
    current_time = current_datetime()
    print('timestamp1: ', timestamp1)
    print('datetime1: ', datetime1)
    print('time_str2: ', time_str2)
    print('timestamp2: ', timestamp2)
    print('datetime3: ', datetime3)
    print('time_str3: ', time_str3)
    print('current_time: ', current_time)
