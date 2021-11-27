from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
from urllib.parse import urlencode, urlparse, urljoin, quote
from config import Target
import re
import cchardet


class CebbankItem(Item):
    target_item = Bs4HtmlField(css_select='#job table.career_list tr')

    bank_name = JsonField(default='光大银行')
    type_main = JsonField(default='社会招聘')

    url = Bs4AttrField(target='href', css_select='td a', many=False)
    name = Bs4TextField(css_select='td a', many=False)
    place = Bs4TextField(css_select='td:nth-of-type(2)', many=False)
    date_publish = Bs4TextField(css_select='td:last-of-type', many=False)

    async def clean_name(self, value):
        list_value = value.split('-')
        self.results['branch_name'] = list_value[0]
        if len(list_value) == 3:
            self.results['position'] = list_value[2]
        return value

    async def clean_url(self, value):
        list_value = value.split('=')
        self.results['job_id'] = list_value[-1]
        return value

    async def clean_date_publish(self, value):
        return value + ' 00:00:00'


class CebbankWorker(Spider):
    name = 'CebbankWorker'
    bank_name = '光大银行'
    begin_url = 'http://cebbank.51job.com/job.php?page='

    async def start_manual(self):
        for index in range(1, 6):
            url = self.begin_url + str(index)
            yield self.request(url=url, method='POST', callback=self.parse)

    async def parse(self, response):
        content = await response.read()
        encoding = cchardet.detect(content)['encoding']
        html = content.decode(encoding, errors='ignore')
        async for item in CebbankItem.get_bs4_items(html=html):
            data = item.results
            target = Target(bank_name=self.bank_name, url=data['url'], metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # CebbankWorker.start()
    pass

