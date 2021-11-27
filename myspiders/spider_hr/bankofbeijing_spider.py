from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target
from urllib.parse import quote, urljoin
import re
from bs4 import BeautifulSoup


# 每次爬取前5页
class BankofbeijingWorker(Spider):
    name = 'BankofbeijingWorker'
    bank_name = '北京银行'
    start_urls = [
        'https://bankofbeijing.zhiye.com/social/?PageIndex=1',
        'https://bankofbeijing.zhiye.com/social/?PageIndex=2',
        'https://bankofbeijing.zhiye.com/social/?PageIndex=3',
        'https://bankofbeijing.zhiye.com/social/?PageIndex=4',
        'https://bankofbeijing.zhiye.com/social/?PageIndex=5',
    ]
    url_detail = 'https://bankofbeijing.zhiye.com'

    async def parse(self, response):
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        list_a = soup.select('.content div.content_wrap a')
        for one in list_a:
            data = {'bank_name': '北京银行', 'type_main': '社会招聘'}
            url = one.get('href')
            if not url.startswith('http'):
                url = self.url_detail + url
            data['url'] = url
            list_url = url.split('=')
            data['job_id'] = list_url[-1]
            data['name'] = one.select_one('.content_wrap_list .content_wrap_list_left h1').get_text(strip=True)
            data['branch_name'] = one.select_one('.content_wrap_list .content_wrap_list_left ul li:first-of-type').get_text(strip=True)
            data['recruit_num'] = one.select_one('.content_wrap_list .content_wrap_list_left ul li:nth-of-type(2)').get_text(strip=True)
            data['place'] = one.select_one('.content_wrap_list .content_wrap_list_left ul li:last-of-type').get_text(strip=True)
            date = one.select_one('.content_wrap_list .content_wrap_list_right p.date').get_text(strip=True)
            data['date'] = date + ' 00:00:00'
            print(data)
            target = Target(bank_name=self.bank_name, url=data['url'], metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # BankofbeijingWorker.start()
    pass

