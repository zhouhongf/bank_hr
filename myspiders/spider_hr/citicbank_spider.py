from config import Target, Job
from myspiders.ruia import JsonField, HtmlField, AttrField, TextField, RegexField, Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField


branch_list = [
    {'branchId': '703220', 'city': '南京'},
    {'branchId': '703260', 'city': '合肥'},
    {'branchId': '703400', 'city': '福州'},
    {'branchId': '711020', 'city': '卡中心'},
    {'branchId': '711100', 'city': '北京'},
    {'branchId': '721100', 'city': '大连'},
    {'branchId': '722100', 'city': '沈阳'},
    {'branchId': '723000', 'city': '天津'},
    {'branchId': '724100', 'city': '石家庄'},
    {'branchId': '725100', 'city': '西安'},
    {'branchId': '726100', 'city': '太原'},
    {'branchId': '727100', 'city': '呼和浩特'},
    {'branchId': '728100', 'city': '南昌'},
    {'branchId': '729100', 'city': '南宁'},
    {'branchId': '730100', 'city': '昆明'},
    {'branchId': '731109', 'city': '上海'},
    {'branchId': '732300', 'city': '苏州'},
    {'branchId': '733600', 'city': '宁波'},
    {'branchId': '733990', 'city': '杭州'},
    {'branchId': '734200', 'city': '厦门'},
    {'branchId': '737001', 'city': '青岛'},
    {'branchId': '737200', 'city': '济南'},
    {'branchId': '738100', 'city': '武汉'},
    {'branchId': '739109', 'city': '郑州'},
    {'branchId': '740110', 'city': '长沙'},
    {'branchId': '741100', 'city': '成都'},
    {'branchId': '742109', 'city': '重庆'},
    {'branchId': '744000', 'city': '广州'},
    {'branchId': '744100', 'city': '深圳'},
    {'branchId': '744809', 'city': '东莞'},
    {'branchId': '745100', 'city': '哈尔滨'},
    {'branchId': '746100', 'city': '兰州'},
    {'branchId': '747109', 'city': '贵阳'},
    {'branchId': '748100', 'city': '长春'},
    {'branchId': '750100', 'city': '乌鲁木齐'},
    {'branchId': '754000', 'city': '海口'},
    {'branchId': '758000', 'city': '银川'},
    {'branchId': '759000', 'city': '西宁'},
    {'branchId': '768100', 'city': '拉萨'}
]


'''
companyName: null
deptOrgName: "海口分行"
education: "硕士研究生"
endDate: "2020-08-17"
hiddenSiteApply: 1
importPost: 0
lastEditDate: null
orgId: 106827
orgName: "海口分行"
outerRecruit: null
postId: 173901
postIdToken: "05d0a66373563bc7"
postName: "信贷管理岗(004406)"
postSyncToXiaojianren: 1
postType: "零售业务"
publishDate: "2020-06-04"
recommendStarOfIr: null
recruitNum: 1
recruitType: 2
serviceCondition: "1.遵纪守法、诚实守信，无违法、违规、违纪等不良记录；
<br>2.全日制硕士研究生及以上学历，年龄33周岁及以下，特别优秀的可放宽至35周岁；                                       
<br>3.具有2年及以上银行工作经验，熟悉个人信贷业务流程；                                                
<br>4.勤奋认真，具有较强的团队协作意识，中共党员且具备档案管理经验者优先；
<br>5.符合履职回避的有关规定。"
subject: "经济学、管理学、法学、理学（数学、统计）、工学（计算机、电子信息、自动化、电气、机械、仪器）、文学（外语、新闻）等相关专业"
workContent: "1.负责用信审查、合同制作、合同审核、用印管理、放款资料管理工作；
<br>2.负责押品管理、抵押登记、押品价值评估、押品评估机构管理；
<br>3.审核征信查询申请，按流程报批后执行查询；
<br>4.审核征信授权资料，规范查询申请上传资料内容，定期开展排查；
<br>5.负责贷后检查管理、风险预警管理、贷后服务等贷后相关工作；
<br>6.负责档案管理、征信管理、内控合规管理等工作；
<br>7.负责反洗钱相关工作。"
workPlace: "海口市,三亚市"
workPlaceCode: "0/4/450/452,0/4/450/453"
workType: "全职"
'''


class CiticbankItem(Item):
    url_detail = 'https://www.hotjob.cn/wt/chinaciticbank/web/index/webPositionN310!getOnePosition?postId=%s&recruitType=2&brandCode=1&importPost=0&columnId=2'
    target_item = JsonField(json_select='postList')

    bank_name = JsonField(default='中信银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='postName')
    job_id = JsonField(json_select='postId')
    branch_name = JsonField(json_select='orgName')
    department = JsonField(json_select='deptOrgName')

    major = JsonField(json_select='subject')
    education = JsonField(json_select='education')
    recruit_num = JsonField(json_select='recruitNum')
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


# 仅爬取前10页即可
class CiticbankWorker(Spider):
    name = 'CiticbankWorker'
    bank_name = '中信银行'
    start_urls = [("https://www.hotjob.cn/wt/chinaciticbank/web/json/position/list?positionType=&comPart=&sicCorpCode=&brandCode=1&releaseTime=0&trademark=0&useForm=&recruitType=2&projectId=&lanType=1&positionName=&workPlace=&keyWord=&xuanJiangStr=&site=&page=" + str(index + 1)) for index in range(10)]

    async def parse(self, response):
        jsondata = await response.json(content_type='text/plain')
        async for item in CiticbankItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)


def start():
    # CiticbankWorker.start()
    pass

