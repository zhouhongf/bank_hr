from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target, Job
from urllib.parse import quote, urljoin

'''
companyName: null
deptOrgName: "浏阳支行"
endDate: "2040-08-10"
hiddenSiteApply: 1
importPost: 1
lastEditDate: null
orgId: 101259
orgName: "浏阳支行"
outerRecruit: null
postId: 102051
postIdToken: "53d622d8c68f2921"
postName: "浏阳支行一级支行副行长岗"
postSyncToXiaojianren: 1
postType: "经营决策序列"
publishDate: "2020-05-27"
recommendStarOfIr: null
recruitType: 2
serviceCondition: "本科及以上学历，经济类、金融类、管理类、法律类或相关专业;年龄40周岁（1980年1月1日之后出生）以下；金融从业3年及以上工作经验，其中1年及以上管理工作经验及1年以上市场营销工作经验；熟悉当地市场金融环境；熟悉银行相关业务知识；熟悉国家相关监管政策、金融法律法规等；优秀的沟通协调能力、分析判断能力、组织计划能力；较强的风险意识与市场意识。"
workContent: "根据支行发展战略、业务经营规划以及经济金融形势的变化，协助组织制定支行全年及阶段性的工作计划，并组织、协调、督促工作计划的实施与落实；协助组织制定和完善支行经营管理的各项规章制度、实施细则和操作流程，并指导监督支行各单位、人员遵照执行。"
workPlace: "长沙市-浏阳市"
workPlaceCode: "0/4/372/374/50197"
workType: "全职，合同工"
'''
class CscbItem(Item):
    url_detail = 'http://bcs.hotjob.cn/wt/BCS/web/index/webPositionN310!getOnePosition?postId=%s&recruitType=2&brandCode=1&importPost=1&columnId=2'
    target_item = JsonField(json_select='postList')

    bank_name = JsonField(default='长沙银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='postName')
    job_id = JsonField(json_select='postId')
    branch_name = JsonField(json_select='orgName')
    department = JsonField(json_select='deptOrgName')

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

    async def clean_recruit_num(self, value):
        if not value:
            return ''
        return str(value)


class CscbWorker(Spider):
    name = 'CscbWorker'
    bank_name = '长沙银行'
    page_size = 10
    start_urls = ['http://bcs.hotjob.cn/wt/BCS/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=0&trademark=0&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&keyWord=&xuanJiangStr=&site=&page=1&isTypeOfSiteSerch=false']
    begin_url = 'http://bcs.hotjob.cn/wt/BCS/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=0&trademark=0&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&keyWord=&xuanJiangStr=&site=&page=%s&isTypeOfSiteSerch=false'

    async def parse(self, response):
        yield self.extract_cscb(response)
        jsondata = await response.json(content_type='text/plain')
        page_count = jsondata['pageCount']
        print('【======== %s ========= 页数：%s】' % (self.name, page_count))

        if page_count > 1:
            for index in range(2, page_count + 1):
                url = self.begin_url % index
                target = Target(bank_name=self.bank_name, url=url)
                await self.redis.insert(field=target.id, value=target.do_dump())

    async def extract_cscb(self, response):
        jsondata = await response.json(content_type='text/plain')
        async for item in CscbItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)


def start():
    # CscbWorker.start()
    pass

