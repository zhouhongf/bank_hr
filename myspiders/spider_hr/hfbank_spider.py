from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
from urllib.parse import urlencode, urlparse, urljoin, quote
import re
from constants import BankDict
from config import Target
import os

'''
Ids: "https://applyjob.chinahr.com/apply/job/wish?jobId=5ebca903c7fd7a04d9bcb256&projectId=5cf735b98534db03dab6a00b"
JobId: ""
PublishDate: "2020-05-14 11:13:17"
gzdd: "济南市"
jiezhiriqi: "2020-06-10"
link: "shzp/zwcx/284564.shtml"
npgw: "专业类-高级专员"
title: "员工发展管理岗"
xuqiubm: "人力资源部（党委组织部）"
zpjg: "总行"
zplb: "社会招聘"

'title': '对公客户经理岗（本部）', 
'xuqiubm': '郑州分行', 
'gzdd': '郑州市', 
'JobId': '', 
'link': 'shzp/zwcx/284260.shtml', 
'npgw': '——', 
'jiezhiriqi': '2020-04-23', 
'Ids': 'https://applyjob.chinahr.com/apply/job/wish?jobId=5e8544cac5dad405596775f8&projectId=5cf735b98534db03dab6a00b', 
'zpjg': '郑州分行', 
'PublishDate': '2020-04-08 09:04:34', 
'zplb': '社会招聘',

'''

class HfbankItem(Item):
    target_item = JsonField(json_select='rows')

    bank_name = JsonField(default='恒丰银行')
    type_main = JsonField(json_select='zplb')

    name = JsonField(json_select='title')
    position = JsonField(json_select='npgw')
    branch_name = JsonField(json_select='zpjg')
    department = JsonField(json_select='xuqiubm')

    url = JsonField(json_select='link')
    date_publish = JsonField(json_select='PublishDate')
    date_close = JsonField(json_select='jiezhiriqi')
    place = JsonField(json_select='gzdd')

    async def clean_date_close(self, value):
        return value + ' 00:00:00'

    async def clean_url(self, value):
        one = os.path.split(value)[-1]
        job_id = one.split('.')[0]
        self.results['job_id'] = job_id
        if not value.startswith('http'):
            value = 'http://career.hfbank.com.cn/' + value
        return value


def make_form_data(page_index: int, page_size: int):
    form_data = {
        'SiteId': '312',
        'col': 'title|link|PublishDate|zpjg|zplb|xuqiubm|gzdd|Ids|JobId|npgw|jiezhiriqi',
        'catalogId': '11190',
        'zpjg': '',
        'npgw': '',
        'newtime': '',
        'jobad_category': '社会招聘',
        'jobad_jobcategory': '',
        'jobad_workingplace': '',
        'search_txt': '',
        'pageIndex': page_index,
        'pagesize': page_size
    }
    return form_data


# 每次爬取前3页
class HfbankWorker(Spider):
    name = 'HfbankWorker'
    bank_name = '恒丰银行'
    start_urls = ['http://career.hfbank.com.cn/ucms/RecruitmentServlet']
    page_size = 10
    form_data = [make_form_data(one + 1, 10) for one in range(3)]
    headers = {'Referer': 'http://career.hfbank.com.cn/shzp/zwcx/index.shtml'}

    async def parse(self, response):
        jsondata = await response.json(content_type='text/html')
        async for item in HfbankItem.get_json(jsondata=jsondata):
            data = item.results
            target = Target(bank_name=self.bank_name, url=data['url'], metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # HfbankWorker.start()
    pass
