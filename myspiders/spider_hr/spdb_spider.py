from myspiders.ruia import JsonField, Item, Spider
import json
from config import Target
from myspiders.tools.tools_spider import fetch_bank_cookies
from urllib.parse import quote, urljoin
import re

'''
address: "上海"
closeDt: "2100-05-31"
deptDescr: "信息科技部"
deptId: "10004822"
desiredStartDt: "2020-05-19"
hpsPronounYN: "Y"
openingsCnt: "若干"
openningJobId: "10005654"
orgnizationId: "10004822"
orgnizationName: "1"
personId: " "
positionName: "创新技术研发岗（物联网架构设计师－创新产品设计）"
posnDescr: "创新技术研发岗（信息科技）"
prmLocArea: "上海"
prmPosition: "01021131"
recuitType: "11"
recuitWay: "1"
statusCode: "010"
'''
class SpdbItem(Item):
    url_detail = 'https://job.spdb.com.cn/jobDetail.do?jobId=%s&type=1'
    target_item = JsonField(json_select='rows')

    bank_name = JsonField(default='浦发银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='positionName')
    job_id = JsonField(json_select='openningJobId')
    branch_name = JsonField(json_select='deptDescr')

    recruit_num = JsonField(json_select='openingsCnt')
    place = JsonField(json_select='address')

    date_publish = JsonField(json_select='desiredStartDt')
    date_close = JsonField(json_select='closeDt')

    async def clean_job_id(self, value):
        self.results['url'] = self.url_detail % value
        return value

    async def clean_date_publish(self, value):
        return value + ' 00:00:00'

    async def clean_date_close(self, value):
        return value + ' 00:00:00'

    async def clean_recruit_num(self, value):
        if not value:
            return ''
        return str(value)

# 每次爬取前5页
class SpdbWorker(Spider):
    name = 'SpdbWorker'
    bank_name = '浦发银行'
    begin_url = 'https://job.spdb.com.cn/socialJobJsonList.do'
    url_list = [('https://job.spdb.com.cn/socialJobJsonList.do?pageNo=%s&deptDescr=&address=&positionName=&recuitType=11&descName=&descType=&jobTime=&jobKey=' % index) for index in range(2, 6)]

    async def start_manual(self):
        self.url_list.insert(0, self.begin_url)
        for url in self.url_list:
            yield self.request(url=url, method='POST', callback=self.parse)

    async def parse(self, response):
        jsondata = await response.json()
        async for item in SpdbItem.get_json(jsondata=jsondata):
            data = item.results
            target = Target(bank_name=self.bank_name, url=data['url'], metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # SpdbWorker.start()
    pass

