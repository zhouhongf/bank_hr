from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target
from urllib.parse import quote, urljoin
import re
from bs4 import BeautifulSoup
import base64

class XacbankItem(Item):
    url_detail = 'https://job.xacbank.com:8001'
    target_item = Bs4HtmlField(css_select='.main_box .recent .recent_box .table_box .com_table table tbody tr')
    bank_name = JsonField(default='西安银行', many=False)
    type_main = Bs4TextField(css_select='td:nth-of-type(2)', many=False)

    name = Bs4TextField(css_select='td a', many=False)
    url = Bs4AttrField(target='href', css_select='td a', many=False)
    place = Bs4TextField(css_select='td:nth-of-type(3)', many=False)

    date_publish = Bs4TextField(css_select='td:nth-of-type(4)', many=False)
    date_close = Bs4TextField(css_select='td:last-of-type', many=False)

    async def clean_name(self, value):
        list_value = value.split('-')
        self.results['branch_name'] = list_value[0]
        self.results['department'] = list_value[1]
        return value

    async def clean_url(self, value):
        if not value.startswith('http'):
            value = self.url_detail + value
        list_value = value.split('=')
        self.results['job_id'] = list_value[-1]
        return value

class XacbankWorker(Spider):
    name = 'XacbankWorker'
    bank_name = '西安银行'
    start_urls = ['https://job.xacbank.com:8001/client/viewnotices/morePostsPage.htm?channel=SO']

    async def parse(self, response):
        html = await response.text()
        async for item in XacbankItem.get_bs4_items(html=html):
            data = item.results
            print(data)
            target = Target(bank_name=self.bank_name, url=data['url'], metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # XacbankWorker.start()
    pass

