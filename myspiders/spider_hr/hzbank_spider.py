from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target, Job
from urllib.parse import quote, urljoin
import re
from bs4 import BeautifulSoup


'''
batchNo: "20191206154854445561"
endTime: "20201231000000"
id: 456734
jobDesc: "1、负责分行公鸡贷面签、云抵贷看房、集中面签、进抵取证、信贷业务首次上门取印、法律文本合同面签等工作。↵2、每日接收被分派的签约任务，做好签约前准备，包括领用待签约法律文本等；↵3、负责按照签约任务列表，上门至客户工作单位签订法律文本。""
jobRequire: "1、大学本科及以上学历，有金融同业工作经验者优先；↵2、遵章守纪，服务意识强，具备较强的沟通能力，有较好的团队合作精神；↵3、条件优异者可适当放宽要求；"
maintenId: "013816"
maintenTime: "20191206000000"
organizationCode: "1101000130"
organizationName: "北京分行"
positionCode: "1101010280"
positionName: "集中作业操作岗"
positionType: "02"
recruitNum: 10
startTime: "20191206000000"
stt: "2"
sttName: null
topFlag: null
transJnlsNo: "20191206154822445560"
workSpace: "北京"
'''

class HzbankItem(Item):
    target_item = JsonField(json_select='content')

    bank_name = JsonField(default='杭州银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='positionName')
    job_id = JsonField(json_select='id')
    url = JsonField(json_select='positionCode')
    branch_name = JsonField(json_select='organizationName')

    recruit_num = JsonField(json_select='recruitNum')
    requirement = JsonField(json_select='jobRequire')
    content = JsonField(json_select='jobDesc')

    place = JsonField(json_select='workSpace')
    date_publish = JsonField(json_select='startTime')
    date_close = JsonField(json_select='endTime')

    async def clean_job_id(self, value):
        return str(value)

    async def clean_date_publish(self, value):
        date = value[0:4] + '-' + value[4:6] + '-' + value[6:8] + ' 00:00:00'
        return date

    async def clean_date_close(self, value):
        date = value[0:4] + '-' + value[4:6] + '-' + value[6:8] + ' 00:00:00'
        return date

    async def clean_recruit_num(self, value):
        if not value:
            return ''
        return str(value)

# 每次爬取前10页
class HzbankWorker(Spider):
    name = 'HzbankWorker'
    bank_name = '杭州银行'
    start_urls = [('https://myjob.hzbank.com.cn/hzzp-apply/service/employInfo/queryEmployInfos?page=%s&positionName=&positionType=02&size=6' % index) for index in range(10)]


    async def parse(self, response):
        jsondata = await response.json(content_type='text/xml')
        async for item in HzbankItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)

def start():
    # HzbankWorker.start()
    pass

