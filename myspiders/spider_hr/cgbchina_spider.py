from myspiders.ruia import JsonField, Item, Spider, Bs4HtmlField, Bs4TextField
from urllib.parse import urlencode, urlparse, urljoin, quote
from config import Job

'''
companyName: null
deptOrgName: "广发总行"
education: "本科"
endDate: "2020-06-10"
hiddenSiteApply: 1
importPost: 0
lastEditDate: null
orgId: 102501
orgName: "广发总行"
outerRecruit: null
postId: 142202
postIdToken: "b3096eb16decddbf"
postName: "总行战略规划部主管（战略管理）"
postSyncToXiaojianren: 1
postType: "战略管理类"
publishDate: "2020-06-02"
recommendStarOfIr: null
recruitNum: 2
recruitType: 2
serviceCondition: "1、大学本科及以上学历；
<br>2、本科学历，5年以上金融工作经验；研究生或以上学历、特别优秀者可适当放宽。有中国人寿工作经历、同业综合金融工作经验者优先；	
<br>3、具备中级职称及以上或等同专业资格证书的优先考虑；	
<br>4、熟悉综合金融或具有某项业务、项目整体推进、协调经验；	
<br>5、具备较好的研究和信息处理能力；
<br>6、具备较强的文字表达和汇总分析能力；
<br>7、思路清晰,并善于总结和分析,能够发现问题,找出解决问题的思路和方向；	
<br>8、具备独立处理事务的管理能力；     
<br>9、具备较强的团队组织和合作能力；	
<br>10、较强的人际沟通能力和协调能力。"
workContent: "1、承接集团公司重振国寿综合化战略，负责制定全行综合金融总体规划及年度要点、计划；		
<br>2、开展综合金融策略研究；	
<br>3、协调各成员单位开展协同业务对接，制定项目推进方案；	
<br>4、研究制定综合金融利益分配及激励机制；
<br>5、推进和督导分行协同试点工作，总结和推广试点经验；	
<br>6、承接、组织集团公司及总行各类综合金融会议、调研；	
<br>7、完成各级领导交办的其他事项。"
workPlace: "广州市"
workPlaceCode: "0/4/396/397"
workType: "全职"
'''

class CgbchinaItem(Item):
    url_detail = 'https://www.hotjob.cn/wt/chinaciticbank/web/index/webPositionN310!getOnePosition?postId=%s&recruitType=2&brandCode=1&importPost=0&columnId=2'
    target_item = JsonField(json_select='postList')

    bank_name = JsonField(default='广发银行')
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


class CgbchinaWorker(Spider):
    name = 'CgbchinaWorker'
    bank_name = '广发银行'

    start_urls = [("https://www.hotjob.cn/wt/chinalife/web/json/position/list?positionType=&comPart=101703&brandCode=1&trademark=0&useForm=0&recruitType=2&lanType=&positionName=&workPlace=&keyWord=&page=" + str(index + 1)) for index in range(5)]

    async def parse(self, response):
        jsondata = await response.json(content_type='text/plain')
        async for item in CgbchinaItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)


def start():
    # CgbchinaWorker.start()
    pass


