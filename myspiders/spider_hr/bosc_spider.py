from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target
from urllib.parse import quote, urljoin
import re
from bs4 import BeautifulSoup



class BoscItem(Item):
    target_item = Bs4HtmlField(css_select='.bg .wrap .right .zwm table tr')

    bank_name = JsonField(default='上海银行')
    type_main = JsonField(json_select='社会招聘')

    name = Bs4TextField(css_select='')
    job_id = JsonField(json_select='postId')
    branch_name = JsonField(json_select='belongsStruName')

    place = JsonField(json_select='placeStr')
    date_publish = JsonField(json_select='publishTime')
    date_close = JsonField(json_select='enterEndTime')

# 每次爬取前5页
class BoscWorker(Spider):
    name = 'BoscWorker'
    bank_name = '上海银行'
    start_urls = ['https://bosc.zhiye.com/social']
    begin_url = 'https://bosc.zhiye.com/social/?PageIndex='
    url_detail = 'https://bosc.zhiye.com'

    async def parse(self, response):
        yield self.extract_bosc(response)

        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        page_count_dom = soup.select_one('.bg .wrap .right .page a:nth-of-type(8)')
        if page_count_dom:
            page_count = page_count_dom.get_text(strip=True)
            page_count = int(page_count)
            print('【======== %s ========= 页数：%s】' % (self.name, page_count))

            if page_count > 1:
                for index in range(2, page_count + 1):
                    url = self.begin_url + str(index)
                    target = Target(bank_name=self.bank_name, url=url)
                    await self.redis.insert(field=target.id, value=target.do_dump())


    async def extract_bosc(self, response):
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        list_tr = soup.select('.bg .wrap .right .zwm table tr')
        for index in range(1, len(list_tr)):
            one = list_tr[index]
            data = {'bank_name': '上海银行', 'type_main': '社会招聘'}
            name_dom = one.select_one('td a')
            data['name'] = name_dom.get_text(strip=True)
            url = name_dom.get('href')
            if not url.startswith('http'):
                url = self.url_detail + url
            data['url'] = url
            list_url = url.split('=')
            data['job_id'] = list_url[-1]
            data['branch_name'] = one.select_one('td:nth-of-type(2)').get_text(strip=True)
            data['place'] = one.select_one('td:nth-of-type(3)').get_text(strip=True)
            date = one.select_one('td:nth-of-type(4)').get_text(strip=True)
            data['date'] = date + ' 00:00:00'
            data['recruit_num'] = one.select_one('td:last-of-type').get_text(strip=True)
            target = Target(bank_name=self.bank_name, url=data['url'], metadata={'data': data}, callback='extract_bosc_next')
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # BoscWorker.start()
    pass

