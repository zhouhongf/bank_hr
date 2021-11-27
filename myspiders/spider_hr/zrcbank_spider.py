from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target, Job
from urllib.parse import quote, urljoin
from bs4 import BeautifulSoup


class ZrcbankWorker(Spider):
    name = 'ZrcbankWorker'
    bank_name = '张家港行'
    start_urls = ['https://zrcbank.zhiye.com/Social']
    url_detail = 'https://zrcbank.zhiye.com'

    async def parse(self, response):
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        list_tr = soup.select('.joblist table.jobsTable tr')
        for index in range(1, len(list_tr)):
            one = list_tr[index]
            data = {'bank_name': '张家港行', 'type_main': '社会招聘'}
            name = one.select_one('td a')
            data['name'] = name.get_text(strip=True)
            url = name.get('href')
            if not url.startswith('http'):
                url = self.url_detail + url
            data['url'] = url
            list_url = url.split('/')
            data['job_id'] = list_url[-1]
            data['place'] = one.select_one('td:nth-of-type(3)').get('title')
            data['date_publish'] = one.select_one('td:last-of-type').get_text(strip=True) + ' 00:00:00'
            target = Target(bank_name=self.bank_name, url=data['url'], metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # ZrcbankWorker.start()
    pass

