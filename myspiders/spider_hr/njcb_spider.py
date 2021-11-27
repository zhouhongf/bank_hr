from myspiders.ruia import Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField, JsonField, RegexField
from urllib.parse import urlencode, urlparse, urljoin, quote
from config import Target
import re
import math


'''
applyExpiredDate: "2021-12-31"
applyReleaseDate: null
bm0000: "1098053"
content: "无锡分行"
e01DeptName: "无锡分行"
e01FullName: "无锡分行理财经理岗"
e01Id: 14399
e01LengthReq: null
e01Req: null
e01ZgReq: "大学本科,硕士研究生,博士研究生"
keyword: null
keywordList: null
major_req: null
outFlag: null
reqCount: 3
workingPlace: "无锡"
zpplanId: 113
zpreqId: 170
zpreqItemId: 1849
zpreqPlanId: null
'''

class NjcbItem(Item):
    url_detail = 'https://job.njcb.com.cn/recruit/api/e01/getE01VoById?e01Id=%s&bm0000=%s&zpreqItemId=%s&reqtype=0'
    target_item = JsonField(json_select='obj>data')

    bank_name = JsonField(default='南京银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='e01FullName')
    job_id = JsonField(json_select='e01Id')
    branch_name = JsonField(json_select='e01DeptName')

    major = JsonField(json_select='major_req')
    education = JsonField(json_select='e01ZgReq')

    recruit_num = JsonField(json_select='reqCount')
    place = JsonField(json_select='workingPlace')
    date_close = JsonField(json_select='applyExpiredDate')

    e01Id = JsonField(json_select='e01Id')
    bm0000 = JsonField(json_select='bm0000')
    zpreqItemId = JsonField(json_select='zpreqItemId')

    async def clean_job_id(self, value):
        return str(value)

    async def clean_date_close(self, value):
        return value + ' 00:00:00'


def make_form_data(page_index: int, page_size: int):
    form_data = {
        'outFlag': '5',
        'workingPlace': '',
        'content': '',
        'deptName': '',
        'applyExpiredDate': '',
        'zgReq': '',
        'keyword': '',
        'page': page_index,
        'rows': page_size,
        'sort': '',
        'order': 'desc'
    }
    return form_data


# 爬取全部页面
class NjcbWorker(Spider):
    name = 'NjcbWorker'
    bank_name = '南京银行'
    start_urls = ['https://job.njcb.com.cn/recruit/api/e01/getListByOutFlag']
    page_size = 10
    form_data = [
        {
            'outFlag': '5',
            'workingPlace': '',
            'content': '',
            'deptName': '',
            'applyExpiredDate': '',
            'zgReq': '',
            'keyword': '',
            'page': 1,
            'rows': 10,
            'sort': '',
            'order': 'desc'
        }
    ]

    async def parse(self, response):
        yield self.extract_njcb(response)

        jsondata = await response.json(content_type='text/html')
        page_count = jsondata['obj']['pages']
        print('【======== %s ========= 页数：%s】' % (self.name, page_count))

        if page_count > 1:
            for index in range(2, page_count + 1):
                formdata = make_form_data(index, self.page_size)
                target = Target(bank_name=self.bank_name, method='POST', url=self.start_urls[0], formdata=formdata)
                await self.redis.insert(field=target.id, value=target.do_dump())

    async def extract_njcb(self, response):
        jsondata = await response.json(content_type='text/html')
        async for item in NjcbItem.get_json(jsondata=jsondata):
            data = item.results
            url_next = NjcbItem.url_detail % (data['e01Id'], data['bm0000'], data['zpreqItemId'])
            target = Target(bank_name=self.bank_name, method='POST', url=url_next, metadata={'data': data}, callback='extract_njcb_next')
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # NjcbWorker.start()
    pass
