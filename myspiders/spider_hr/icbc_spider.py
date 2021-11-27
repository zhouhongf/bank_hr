from myspiders.ruia import Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField, JsonField, RegexField
from urllib.parse import urlencode, urlparse, urljoin, quote
from config import Target
import re
import math


class IcbcItem(Item):
    url_next = 'https://job.icbc.com.cn/pc/index.html#/main/social/postDetail/'
    pattern_date = re.compile(r'20[0-9]{2}\-[01][0-9]\-[0123][0-9]')

    target_item = JsonField(json_select='data>dataList')

    bank_name = JsonField(default='工商银行')
    name = JsonField(json_select='publishPostName')
    job_id = JsonField(json_select='postId')
    branch_name = JsonField(json_select='belongsStruName')
    type_main = JsonField(json_select='recruitTypeStr')
    place = JsonField(json_select='placeStr')
    date_publish = JsonField(json_select='publishTime')
    date_close = JsonField(json_select='enterEndTime')

    async def clean_job_id(self, value):
        self.results['url'] = self.url_next + value
        return value


def make_form_data_list(page_count: int):
    form_data = [
        {
            "public": {"call_app": "F-TRM"},
            "private": {"pageSize": 10, "page": index, "struIds": "", "recruitType": "R00302"}
        } for index in range(2, page_count + 1)
    ]
    return form_data


# 爬取全部页面
class IcbcWorker(Spider):
    name = 'IcbcWorker'
    bank_name = '工商银行'
    start_urls = ['https://job.icbc.com.cn/icbc/trmo/post/qryPostList']
    page_size = 10
    form_data = [
        {"public": {"call_app": "F-TRM"},
         "private": {"pageSize": 10, "page": 1, "struIds": "", "recruitType": "R00302"}}
    ]
    form_data_type = 'json'

    async def parse(self, response):
        yield self.extract_icbc(response)

        jsondata = await response.json()
        total = jsondata['data']['total']
        page_count = math.ceil(total / self.page_size)
        print('【======== %s ========= 页数：%s】' % (self.name, page_count))

        if page_count > 1:
            formdatas = make_form_data_list(page_count)
            for formdata in formdatas:
                target = Target(bank_name=self.bank_name, method='POST', url=self.start_urls[0], formdata=formdata, formdata_type='json')
                await self.redis.insert(field=target.id, value=target.do_dump())


    async def extract_icbc(self, response):
        jsondata = await response.json()
        async for item in IcbcItem.get_json(jsondata=jsondata):
            data = item.results
            url_next = data['url']
            target = Target(bank_name=self.bank_name, url=url_next, metadata={'data': data}, request_type='pyppeteer', callback='extract_icbc_next')
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # IcbcWorker.start()
    pass


