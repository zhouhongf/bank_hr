from myspiders.ruia import JsonField, Item, Spider
from config import Target
import math
from copy import copy
from config import Job

'''
businessUnitId: "PA012"
businessUnitName: "平安金服"
campusTalkId: ""
channelId: "1"
createdBy: "ZHAOYANAN123"
createdDate: "2020-03-01 20:47:23"
deptId: "S000048875"
deptName: "金服西安分公司"
deptShowName: "平安金服西安分公司"
duty: "1. 薪酬核算：负责分公司各部门每月薪酬数据核实，数据理算，保证薪酬核算工作精确开展；↵2. 薪酬分析：对分公司各业务条线薪酬数据进行分析，从薪酬数据中挖掘和检视经营问题，输出有效的管理建议；↵3. 薪酬规划：负责分公司各岗位薪酬规划工作，结合职位特点及相关人事规定，精准核定各岗位薪酬标准。"
education: "本科"
educationCode: "0/606/612"
idPosition: "e15429dc317630ca8225116756ebfa72"
internshipMax: ""
internshipMin: ""
interviewCity: "线上面试"
interviewCityCode: ""
interviewCityOther: "线上面试"
interviewCityOtherCode: "线上面试"
interviewCityOverseas: ""
overseasWorkCity: ""
overseasWorkCityCode: ""
platFormId: ""
positionCategoryId: "c213f309a7fa3eb481673ce9f59828ea"
positionCategoryName: "管培类"
positionCode: "x12310I"
positionName: "西安分公司薪酬管理岗"
positionType: "全职"
positionTypes: ""
publishDate: "2020-06-04 10:17:45"
publishStatus: "P"
publishStatusDesc: "已发布"
qualification: "1. 本科及以上学历，专业不限，有相关岗位实习经验为佳；↵2. 个性沉稳，仔细认真，数据敏感度佳。"
recruitNumber: 1
salaryMax: null
salaryMin: null
salaryType: "C/SALARY/TYPE/NEGOTIABLE"
salaryTypeDesc: "面议"
shortDesc: ""
stickDate: ""
stickPositionThirdId: ""
stickStatus: ""
structureId: "PA012S000048875"
tenantId: "CHDUIE8QRPG16AJFM2B9NL0OS3TK574"
updatedBy: "ZHAOYANAN123"
updatedDate: "2020-06-04 10:17:45"
workCity: "西安市"
workCityCode: "0/4/489/491"
workCityOverseas: ""
'''


class PinganItem(Item):
    url_detail = 'http://campus.pingan.com/positionDetail?positionId='

    target_item = JsonField(json_select='data>list')
    bank_name = JsonField(default='平安银行')
    type_main = JsonField(default='校园招聘')

    name = JsonField(json_select='positionName')
    job_id = JsonField(json_select='idPosition')
    branch_name = JsonField(json_select='businessUnitName')
    department = JsonField(json_select='deptShowName')

    education = JsonField(json_select='education')
    recruit_num = JsonField(json_select='recruitNumber')
    requirement = JsonField(json_select='qualification')
    content = JsonField(json_select='duty')

    place = JsonField(json_select='workCity')

    date_publish = JsonField(json_select='publishDate')

    async def clean_job_id(self, value):
        self.results['url'] = self.url_detail + value
        return value

    async def clean_recruit_num(self, value):
        if not value:
            return ''
        return str(value)


def make_form_data(wecruitId: str, page_index: int, page_size: int):
    formdata = {
        "PageNum": page_index,
        "businessUnitId": "",
        "pageSize": page_size,
        "positionCategoryId": "",
        "wecruitId": wecruitId,
        "positionType": "1",
        "wecruitPlatform": 'true',
        "workCity": "",
        "interviewCity": ""
    }
    return formdata


# 爬取前10页
class PinganWorker(Spider):
    url_first = 'http://campus.pingan.com/zztj-recruit-talent-webserver/rctt/candidate/officialWebsite/queryOfficialIdByUrl'
    begin_url = 'http://campus.pingan.com/zztj-recruit-talent-webserver/rctt/candidate/position/campus/positionSearch/queryPositionPage'
    name = 'PinganWorker'
    bank_name = '平安银行'
    page_size = 10

    async def start_manual(self):
        formdata = {"officialUrl": "", "recruitType": "3"}
        yield self.request(url=self.url_first, method='POST', formdata=formdata, formdata_type='json', callback=self.parse)

    async def parse(self, response):
        jsondata = await response.json()
        wecruitId = jsondata['data']['wecruitId']
        for index in range(1, 11):
            formdata = make_form_data(wecruitId=wecruitId, page_index=index, page_size=self.page_size)
            yield self.request(url=self.begin_url, method='POST', formdata=formdata, formdata_type='json', callback=self.parse_list)

    async def parse_list(self, response):
        jsondata = await response.json()
        async for item in PinganItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)


def start():
    # PinganWorker.start()
    pass
