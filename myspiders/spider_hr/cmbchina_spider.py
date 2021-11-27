from myspiders.ruia import JsonField, AttrField, Item, Spider
from urllib.parse import urlencode, urlparse
from config import CONFIG, Target, Job
import random
import demjson
import re
import os

'''
AIResumeCount: 0
ActivityGID: null
ActivityTitle: ""
ApprovedBy: ""
ApprovedComment: "请明确数字的包含关系，重新提交审批"
ApprovedOn: "2020-04-02T16:42:51.593"
ApprovedOnfb: "0001-01-01T00:00:00"
BeginAge: 0
BranchCode: "108019"
BranchCodeName: ""
CollegeRequirement: ""
CollegeRequirementName: ""
Count: 0
DeleteFilterRules: null
DySynchronizationStatus: 0
EducationRequirement: ""
EducationRequirementGID: ""
EducationRequirementName: ""
EndAge: 0
ExpiredOn: "2020-12-31T00:00:00"
ExpiredOnStr: "2020-12-31"
FilledPositions: 0
FilterRules: null
FromType: "social"
GenderRequirement: ""
IsForever: null
IsHeadhunter: null
IsSocialView: false
JobCategory: ""
JobCategoryGID: ""
JobCategoryName: ""
JobCode: ""
JobDescription: ""
JobDisplay: "支行行长"
JobDisplayShowPaper: ""
JobGID: "01435e0d-60e6-4d9c-add9-1025fee76927"
JobName: "支行行长|行长室"
JobNameGID: ""
JobRequirement: "<p>1.年龄40岁（含）以下，全日制大学本科及以上学历；</p><p>2.5年及以上银行从业经验，3年及以上银行网点零售业务管理经验；</p><p>3.较强的业务开拓、风险把控、团队管理和综合协调能力；</p><p>4.具有良好的品质和职业操守，无不良、违纪和违法行为纪录；</p><p>5.特别优秀者，以上条件可适当放宽。</p>"
JobResponsibility: "<p>1.统筹支行零售经营管理目标，完成综合绩效考核指标；</p><p>2.负责支行零售各项营销工作，树立良好服务品牌，建立和维护与重要客户的关系，不断拓展市场份额；</p><p>3.负责支行内控合规、安全保卫、综合事务等工作。</p>"
JobType: ""
JobTypeName: ""
Location: "贵阳市"
LocationGID: ""
LocationName: ""
MajorRequirement: ""
MajorRequirementName: ""
OpenPositions: 0
OrgID: ""
OrgName: "贵阳分行"
Owner: ""
OwnerEmail: ""
OwnerPhone: ""
PositionsRate: 0
PresentRequirement: ""
PresentRequirementName: ""
PublishGID: "565c6374-5029-4bde-8fd2-61cfbcddc59f"
PublishIsDistributionChannels: false
PublishIsPersonnelExchangeCentre: false
PublishedOn: "2020-03-31T00:00:00"
PublishedOnStr: "2020-03-31"
RecruitJobTypeID: 1
RecruitJobTypeName: ""
RecruitmentTypeID: null
RecruitmentTypeName: ""
Remark: ""
RequireDept: ""
RequireDeptName: ""
RequireGroup: ""
RowCreated: "2020-03-30T18:15:59.45"
RowCreatedBy: ""
RowCreatedByName: ""
RowDeleted: null
RowDeletedBy: ""
RowIsDeleted: null
RowUpdated: "0001-01-01T00:00:00"
RowUpdatedBy: ""
SalaryRange: ""
SalaryRangeGID: ""
ShowTab: 0
Status: 3
StatusStr: "已审核"
Synchronization: ""
TalentRecruitmentStatus: 0
TolalPositions: 0
UpdateCallbackStatus: ""
WarnState: ""
WorkingYears: null
WorkingYearsName: ""
isAdd: false
isaudit: false
job: ""
job_id: ""
longtermsocial: 0
score: 0
'''


class CmbchinaItem(Item):
    url_detail = 'http://career.cmbchina.com/index.html#jobDetail?id=%s&returnUrl=#jobList?id=1'

    target_item = JsonField(json_select='Result')

    bank_name = JsonField(default='招商银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='JobDisplay')
    job_id = JsonField(json_select='JobGID')
    branch_name = JsonField(json_select='OrgName')
    department = JsonField(json_select='JobName')

    subject = JsonField(json_select='MajorRequirementName')
    education = JsonField(json_select='EducationRequirementName')

    requirement = JsonField(json_select='JobRequirement')
    content = JsonField(json_select='JobResponsibility')

    place = JsonField(json_select='Location')
    date_publish = JsonField(json_select='PublishedOnStr')
    date_close = JsonField(json_select='ExpiredOnStr')

    async def clean_date_publish(self, value):
        return value + ' 00:00:00'

    async def clean_date_close(self, value):
        return value + ' 00:00:00'


def make_form_data(page_count: int):
    formdata_list = []
    for one in range(page_count):
        formdata = {"branchCode": "", "pageIndex": one + 1, "pageSize": 6, "recruitJobTypeID": "1", "searchWords": "", "location": ""}
        formdata_list.append(formdata)
        formdata_extra = {"branchCode": "", "pageIndex": one + 1, "pageSize": 6, "recruitJobTypeID": "0", "searchWords": "", "location": ""}
        formdata_list.append(formdata_extra)
    return formdata_list


# 每次爬取前10页
class CmbchinaWorker(Spider):
    name = 'CmbchinaWorker'
    bank_name = '招商银行'
    page_size = 6
    start_urls = ['http://career.cmbchina.com/api/JobPublish/GetJobPublishList']
    form_data = make_form_data(10)
    form_data_type = 'json'

    async def parse(self, response):
        jsondata = await response.json()
        async for item in CmbchinaItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job)


def start():
    # CmbchinaWorker.start()
    pass
