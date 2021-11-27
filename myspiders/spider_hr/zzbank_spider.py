from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField
import json
from config import Target, Job
from urllib.parse import quote, urljoin

'''
companyName: null
deptOrgName: "分支机构"
endDate: "3000-01-01"
hiddenSiteApply: 1
importPost: 0
lastEditDate: null
orgId: 100002
orgName: "分支机构"
outerRecruit: null
postId: 100648
postIdToken: "212bac298ad81dd8"
postName: "小微客户经理"
postSyncToXiaojianren: 1
postType: "分支机构零售"
publishDate: "2020-04-23"
recommendStarOfIr: null
recruitType: 2
serviceCondition: "1、年龄35岁以下；
<br>2、全日制本科及以上学历，金融、经济、营销、管理类相关专业；
<br>3、3年以上银行从业经历，1年以上小微客户经理岗位从业经历，具有直接拓客工作经历；
<br>4、熟悉当地各类市场和商圈情况，具有较强的市场拓展能力和风险防范意识；
<br>5、具备较强的客户服务和营销意识，具备管理和开发客户的能力。"
workContent: "1、负责零售信贷客户的营销和开发工作；
<br>2、负责零售信贷客户的服务和维护工作；
<br>3、负责零售信贷客户的贷后检查工作；
<br>4、完成零售业务或产品销售任务。"
workPlace: "郑州市"
workPlaceCode: "0/4/331/333"
workType: "全职"
'''
class ZzbankItem(Item):
    url_detail = 'http://www.hotjob.cn/wt/zzbank/web/index/webPositionN300!getOnePosition?postId=%s&recruitType=2&brandCode=1&columnId=2&importPost=0'
    target_item = JsonField(json_select='postList')

    bank_name = JsonField(default='郑州银行')
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


class ZzbankWorker(Spider):
    name = 'ZzbankWorker'
    bank_name = '郑州银行'
    page_size = 10
    start_urls = ['http://www.hotjob.cn/wt/zzbank/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=&trademark=1&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&page=1&site=&keyWord=']
    begin_url = 'http://www.hotjob.cn/wt/zzbank/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=&trademark=1&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&page=%s&site=&keyWord='

    async def parse(self, response):
        yield self.extract_zzbank(response)
        jsondata = await response.json(content_type='text/plain')
        page_count = jsondata['pageCount']
        print('【======== %s ========= 页数：%s】' % (self.name, page_count))

        if page_count > 1:
            for index in range(2, page_count + 1):
                url = self.begin_url % index
                target = Target(bank_name=self.bank_name, url=url)
                await self.redis.insert(field=target.id, value=target.do_dump())

    async def extract_zzbank(self, response):
        jsondata = await response.json(content_type='text/plain')
        async for item in ZzbankItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)


def start():
    # ZzbankWorker.start()
    pass

