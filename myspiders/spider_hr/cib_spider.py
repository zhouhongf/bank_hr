from myspiders.ruia import JsonField, AttrField, Item, Spider
from urllib.parse import urlencode, urlparse
from config import CONFIG, Target, Job
import random
import demjson
import re
import os

'''
companyName: null
deptOrgName: "天津分行"
education: "本科"
endDate: "2020-08-30"
hiddenSiteApply: 1
importPost: 0
lastEditDate: null
orgId: 100607
orgName: "天津分行"
outerRecruit: null
postId: 104807
postIdToken: "cf2b89cba492e60e"
postName: "市场营销类岗位"
postSyncToXiaojianren: 1
postType: "营销类"
publishDate: "2020-03-03"
recommendStarOfIr: null
recruitType: 1
serviceCondition: "1、国内院校2020年应届毕业生（须于2020年8月31日前毕业），海外院校毕业生2019年1月1日至2020年8月31日前毕业生；
<br>2、遵纪守法，诚实守信，具有良好的道德品质，无不良纪录；
<br>3、形象气质佳，具有较强的责任心、执行能力和沟通表达能力、良好的职业操守；
<br>4、具有较强的市场敏感性、产品推广能力及风险意识。"
subject: "金融类、财会类、经济类、市场营销相关专业"
workContent: "1、开展市场调研、调查工作， 深入了解客户需求，为客户提供专业化优质服务；
<br>2、参与本行业务调查、搜集客户资料，进行客户需求分析；协助客户经理进行产品组合设计、流程控制安排、服务定价评估等，形成规范完整的金融服务方案，对客户进行深度开发，最大程度挖掘客户业务潜力；
<br>3、经营服务管辖分行级战略客户，包括客户营销、客户关系维护、客户经营规划、客户视图建设、集团授信、服务方案制定及实施等；协助客户经理及各级机构战略客户及下属成员提供金融服务；
<br>4、收集相关业务等方面需求信息，开展创新产品的设计、开发；组织落实重点产品运用，并对产品运作情况进行跟踪管理；
<br>5、参与本行开展各种形式的营销活动与宣传活动，根据业务导向进行营销宣传活动方案，并适时开展相关业务与产品的营销推介。"
workPlace: "天津市"
workPlaceCode: "0/4/12/13"
workType: ""
'''


class CibItem(Item):
    url_detail = 'https://sc.hotjob.cn/wt/CIB/web/index/webPositionN310!getOnePosition?postId=%s&recruitType=1&brandCode=1&importPost=0&columnId=1'
    target_item = JsonField(json_select='postList')

    bank_name = JsonField(default='兴业银行')
    type_main = JsonField(default='校园招聘')

    name = JsonField(json_select='postName')
    job_id = JsonField(json_select='postId')
    branch_name = JsonField(json_select='orgName')
    department = JsonField(json_select='deptOrgName')

    major = JsonField(json_select='subject')
    education = JsonField(json_select='education')

    requirement = JsonField(json_select='serviceCondition')
    content = JsonField(json_select='workContent')

    place = JsonField(json_select='workPlace')

    date_publish = JsonField(json_select='publishDate')
    date_close = JsonField(json_select='endDate')

    async def clean_job_id(self, value):
        self.results['url'] = self.url_detail % value
        return str(value)

    async def clean_date_publish(self, value):
        return value + ' 00:00:00'

    async def clean_date_close(self, value):
        return value + ' 00:00:00'


# 每次爬取前3页
class CibWorker(Spider):
    name = 'CibWorker'
    bank_name = '兴业银行'
    page_size = 10
    start_urls = [
        'https://sc.hotjob.cn/wt/CIB/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=0&trademark=0&useForm=&recruitType=1&projectId=&lanType=1&positionName=&workPlace=&keyWord=&xuanJiangStr=&site=&page=1',
        'https://sc.hotjob.cn/wt/CIB/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=0&trademark=0&useForm=&recruitType=1&projectId=&lanType=1&positionName=&workPlace=&keyWord=&xuanJiangStr=&site=&page=2',
        'https://sc.hotjob.cn/wt/CIB/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=0&trademark=0&useForm=&recruitType=1&projectId=&lanType=1&positionName=&workPlace=&keyWord=&xuanJiangStr=&site=&page=3',
    ]

    async def parse(self, response):
        jsondata = await response.json(content_type='text/plain')
        async for item in CibItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)


def start():
    # CibWorker.start()
    pass
