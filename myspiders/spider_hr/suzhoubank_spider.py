from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target
from urllib.parse import quote, urljoin
import re
from bs4 import BeautifulSoup
import base64

''' 
<script type="text/javascript">
    var basePath="/zpWeb";
    var token="df024287";
</script>
'''
class SuzhoubankWorker(Spider):
    name = 'SuzhoubankWorker'
    bank_name = '苏州银行'
    start_urls = ['http://hr.suzhoubank.com/zpWeb/zpweb/planList.do?actPara=findMoreHeadJob']
    url_detail = 'http://hr.suzhoubank.com'
    pattern = re.compile(r'var token="(.+?)"')
    url_referer = 'http://hr.suzhoubank.com/zpWeb/zpweb/planList.do?actPara=findMoreHeadJob'

    async def parse(self, response):
        html = await response.text()
        result = self.pattern.search(html)
        csrftoken = ''
        if result:
            token = result.group(1)
            btoken = bytes(token, 'utf-8')
            csrftoken = base64.b64encode(btoken).decode()

        soup = BeautifulSoup(html, 'lxml')
        list_tr = soup.select('form table.table tr')
        for index in range(1, len(list_tr)):
            one = list_tr[index]
            data = {'bank_name': '苏州银行'}
            data['type_main'] = one.select_one('td:first-of-type').get_text(strip=True)
            name_dom = one.select_one('td a')
            data['name'] = name_dom.get_text(strip=True)
            url = name_dom.get('href')
            if not url.startswith('http'):
                url = self.url_detail + url
            if csrftoken:
                url = url + '&csrftoken=' + csrftoken
                self.url_referer = self.url_referer + '&csrftoken=' + csrftoken
            data['url'] = url
            data['job_id'] = url
            data['branch_name'] = one.select_one('td:nth-of-type(3)').get_text(strip=True)
            data['department'] = one.select_one('td:nth-of-type(4)').get_text(strip=True)
            data['place'] = one.select_one('td:nth-of-type(5)').get_text(strip=True)
            data['recruit_num'] = one.select_one('td:nth-of-type(6)').get_text(strip=True)
            date = one.select_one('td:last-of-type').get_text(strip=True)
            data['date'] = date + ' 00:00:00'
            headers = {'Referer': self.url_referer}
            target = Target(bank_name=self.bank_name, url=data['url'], headers=headers, metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # SuzhoubankWorker.start()
    pass

