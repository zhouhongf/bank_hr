import re
import hashlib
import random


def random_digits(length):
    list = []
    for i in range(int(length)):
        list.append(str(random.randrange(10)))
    digits = ''.join(list)
    return digits


# str就是unicode了.Python3中的str对应2中的Unicode
def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


# 从字符串中提取出数字
def extract_num(text):
    match_re = re.match(".*?(\d+).*", text)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


# 从包含,的字符串中提取出数字
def extract_num_include_dot(text):
    text_num = text.replace(',', '')
    try:
        nums = int(text_num)
    except:
        nums = -1
    return nums


