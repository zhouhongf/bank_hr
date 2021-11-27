from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
from urllib.parse import urlencode, urlparse, urljoin, quote
from bs4 import BeautifulSoup
from config import Target


class HxbItem(Item):
    bank_name = JsonField(default='广发银行')
    type_main = Bs4TextField(css_select='td:first-of-type')

    name = Bs4TextField(css_select='td:nth-of-type(2)')
    url = Bs4AttrField(target='href', css_select='td:nth-of-type(2) a')

    branch_name = Bs4TextField(css_select='td:nth-of-type(3)')
    place = Bs4TextField(css_select='td:nth-of-type(4)')
    recruit_num = Bs4TextField(css_select='td:nth-of-type(5)')

    date_close = Bs4TextField(css_select='td:last-of-type')

    async def clean_url(self, value):
        list_value = value.split('=')
        self.results['job_id'] = list_value[-1]
        return value

    async def clean_date_close(self, value):
        return value + ' 00:00:00'


class HxbWorker(Spider):
    name = 'HxbWorker'
    bank_name = '华夏银行'
    start_urls = ['https://zhaopin.hxb.com.cn/zpWeb/zpweb/planList.do?actPara=findMoreHeadJob']

    async def parse(self, response):
        url_old = response.url
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        list_row = soup.select('table tr td form table.table tr')
        for index in range(1, len(list_row)):
            row = list_row[index]
            data = {'bank_name': '广发银行'}
            data['type_main'] = row.select_one('td:first-of-type').get_text(strip=True)
            data['name'] = row.select_one('td:nth-of-type(2)').get_text(strip=True)
            url = row.select_one('td:nth-of-type(2) a').get('href')
            if not url.startswith('http'):
                url = urljoin(url_old, url)
            data['url'] = url
            data['job_id'] = url.split('=')[-1]

            data['branch_name'] = row.select_one('td:nth-of-type(3)').get_text(strip=True)
            data['place'] = row.select_one('td:nth-of-type(4)').get_text(strip=True)
            data['recruit_num'] = row.select_one('td:nth-of-type(5)').get_text(strip=True)
            data['date_close'] = row.select_one('td:last-of-type').get_text(strip=True) + ' 00:00:00'

            target = Target(bank_name=self.bank_name, url=data['url'], metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # HxbWorker.start()
    pass

