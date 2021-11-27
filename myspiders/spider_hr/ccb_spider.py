import math
from config import CONFIG, Target
import os
import re
from myspiders.ruia import JsonField, Item, Spider, Bs4AttrField
from urllib.parse import urlencode, urlparse, urljoin, quote


'''collectId: "0"
currentApply: "0"
endDate: "2020-04-26"
firstApply: "0"
isCollect: "0"
orgId: "2011629"
orgName: "贵州省分行"
planId: "2020033119781053"
planPost: "20200331211342345765"
planPostName: "智能电气管控岗"
planStatus: "2"
planType: "SH"
postDate: "2020-04-03 16:30:12"
secondApply: "0"
secondOName: "贵州省分行本部"
secondOrgId: "20200325192118188540"
workPlace: "贵州省贵阳市市辖区"'''


class CcbItem(Item):
    url_next_list = 'http://job.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&isAjaxRequest=true&SERVLET_NAME=WCCMainPlatV5&TXCODE=NHR104&keyWord=&planType=SH&orgId=&planPostId=&planId=&PAGE_JUMP=%s&REC_IN_PAGE=10'
    url_next_detail = 'http://job.ccb.com/cn/job/job_detail.html?planId=%s&planPost=%s&planType=%s&orgId=%s&secondOrgId=%s&'

    target_item = JsonField(json_select='planPostList')

    bank_name = JsonField(default='建设银行')
    type_main = JsonField(default='社会招聘')
    name = JsonField(json_select='planPostName')

    job_id = JsonField(json_select='planId')
    branch_name = JsonField(json_select='orgName')
    department = JsonField(json_select='secondOName')

    place = JsonField(json_select='workPlace')
    date_publish = JsonField(json_select='postDate')
    date_close = JsonField(json_select='endDate')

    planId = JsonField(json_select='planId')
    planPost = JsonField(json_select='planPost')
    planType = JsonField(json_select='planType')
    orgId = JsonField(json_select='orgId')
    secondOrgId = JsonField(json_select='secondOrgId')

    async def clean_date_close(self, value):
        return value + ' 00:00:00'


class CcbWorker(Spider):
    name = 'CcbWorker'
    bank_name = '建设银行'
    headers = {'Referer': 'http://job.ccb.com/cn/job/plan_index.html?planType=SH'}
    page_size = 10
    start_urls = ['http://job.ccb.com/tran/WCCMainPlatV5?CCB_IBSVersion=V5&isAjaxRequest=true&SERVLET_NAME=WCCMainPlatV5&TXCODE=NHR104&keyWord=&planType=SH&orgId=&planPostId=&planId=&PAGE_JUMP=1&REC_IN_PAGE=10']

    async def parse(self, response):
        yield self.extract_ccb(response)

        jsondata = await response.json(content_type='text/html')
        page_total = jsondata['TOTAL_PAGE']
        page_count = int(page_total)
        print('【======== %s ========= 页数：%s】' % (self.name, page_count))

        if page_count > 1:
            for index in range(2, page_count + 1):
                url = CcbItem.url_next_list % index
                target = Target(bank_name=self.bank_name, url=url, headers=self.headers)
                await self.redis.insert(field=target.id, value=target.do_dump())

    async def extract_ccb(self, response):
        jsondata = await response.json(content_type='text/html')
        async for item in CcbItem.get_json(jsondata=jsondata):
            data = item.results
            url_next = CcbItem.url_next_detail % (data['planId'], data['planPost'], data['planType'], data['orgId'], data['secondOrgId'])
            target = Target(bank_name=self.bank_name, url=url_next, request_type='splash', callback='extract_ccb_next', metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())



def start():
    # CcbWorker.start()
    pass

