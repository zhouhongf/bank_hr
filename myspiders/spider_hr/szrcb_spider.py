from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target, Job
from urllib.parse import quote, urljoin

'''
companyName: null
deptOrgName: "兴化支行"
education: "本科"
endDate: "3000-01-01"
hiddenSiteApply: 1
importPost: 0
lastEditDate: null
orgId: 100385
orgName: "苏州农商银行"
outerRecruit: null
postId: 105103
postIdToken: "76d5ab6bed53d23b"
postName: "苏州农商银行—零售负责人（兴化支行）"
postSyncToXiaojianren: 1
postType: "团队长"
publishDate: "2020-05-29"
recommendStarOfIr: null
recruitType: 2
serviceCondition: "1、年龄40周岁以下，本科及以上学历；
<br>2、具有5年以上银行业务营销和管理经验，有丰富的金融知识和实践经验，较强的政策理论水平与市场营销能力； 
<br>3、在所报岗位区域有客户资源者优先。"
workContent: "1、根据支行营销目标进行市场开拓，维护新老客户，营销公司产品及服务，完成业绩指标；
<br>2、分析行业动态和金融产品，加强团队人员业务培训和营销指导，增强团队建设和管理；
<br>3、负责监督执行风险防范措施，实施关键风险点控制，提高风险管理能力。"
workPlace: "泰州市-兴化市"
workPlaceCode: "0/4/135/189/51873"
workType: "全职"
'''
class SzrcbItem(Item):
    url_detail = 'http://www.hotjob.cn/wt/sznsh/web/index/webPositionN300!getOnePosition?postId=%s&recruitType=2&brandCode=1&columnId=2&importPost=0'
    target_item = JsonField(json_select='postList')

    bank_name = JsonField(default='苏农银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='postName')
    job_id = JsonField(json_select='postId')
    branch_name = JsonField(json_select='orgName')
    department = JsonField(json_select='deptOrgName')
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

    async def clean_recruit_num(self, value):
        if not value:
            return ''
        return str(value)


class SzrcbWorker(Spider):
    name = 'SzrcbWorker'
    bank_name = '苏农银行'
    page_size = 10
    start_urls = ['http://www.hotjob.cn/wt/sznsh/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=&trademark=1&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&page=1&site=&keyWord=']
    begin_url = 'http://www.hotjob.cn/wt/sznsh/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=&trademark=1&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&page=%s&site=&keyWord='

    async def parse(self, response):
        yield self.extract_szrcb(response)
        jsondata = await response.json(content_type='text/plain')
        page_count = jsondata['pageCount']
        print('【======== %s ========= 页数：%s】' % (self.name, page_count))

        if page_count > 1:
            for index in range(2, page_count + 1):
                url = self.begin_url % index
                target = Target(bank_name=self.bank_name, url=url)
                await self.redis.insert(field=target.id, value=target.do_dump())

    async def extract_szrcb(self, response):
        jsondata = await response.json(content_type='text/plain')
        async for item in SzrcbItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)


def start():
    # SzrcbWorker.start()
    pass

