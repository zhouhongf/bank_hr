from myspiders.ruia import Spider, JsonField, Item
from config import Target
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from myspiders.tools.tools_spider import fetch_bank_cookies

'''
baseCond: "（一）遵纪守法，诚信负责，勤奋务实；
↵（二）身体健康，品貌端正，具有良好的心理素质和抗压能力；
↵（三）大学本科及以上学历；
↵（四）年龄在38周岁及以下；
↵（五）具有2年及以上全职工作经历，且具备岗位所要求的专业知识、从业经历和业务能力；
↵（六）具有较强的责任意识、团队合作精神及良好的沟通、协同能力；
↵（七）具有良好的个人品质与职业道德，无不良从业记录；
↵（八）符合浙商银行亲属回避的要求。"
collegeCond: ""
countOrg: ""
createTime: "2020-02-26"
currentStep: ""
eduCond: "6000600007"
firstName: ""
location: "01065101"
majorCond: "计算机相关专业"
mgrOrg: "f5ce918a001636140ed590a611de89a4"
name: "科技岗"
nativeCond: "不限"
needDept: "0e4d03c4001636140ed590a711de89a4"
needNum: "1"
needOrg: "e4a87749001636140ed5961c11deb193"
note: ""
orgName: ""
planId: "8a8340e96d350d1d01707b7e66940741"
planStatus: ""
postClass: ""
postCond: "1.计算机相关专业本科及以上学历，具有较强的计算机专业能力；
↵2.具有4年及以上网络维护、办公系统维护等计算机相关工作经历，具有银行科技工作经验为佳；
↵3.具有一定网络基础，取得思科认证或华为认证等网络证书者优先。"
postId: "8a8340e96d350d1d01707b82909a0744"
postOrder: "002"
postStatus: "1"
postType: "SH"
remark: ""
secondName: ""
sexCond: "不限"
'''

class CzbankItem(Item):
    url_detail = 'https://zp.czbank.com.cn/zpweb/zpPostController/jobDetailPage.mvc?postId='
    target_item = JsonField(json_select='dataList')

    bank_name = JsonField(default='浙商银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='name')
    job_id = JsonField(json_select='postId')

    major = JsonField(json_select='majorCond')
    education = JsonField(json_select='collegeCond')

    recruit_num = JsonField(json_select='needNum')
    requirement = JsonField(json_select='postCond')

    date_publish = JsonField(json_select='createTime')

    async def clean_job_id(self, value):
        self.results['url'] = self.url_detail + value
        return str(value)

    async def clean_date_publish(self, value):
        return value + ' 00:00:00'

    async def clean_recruit_num(self, value):
        if not value:
            return ''
        return str(value)


class CzbankWorker(Spider):
    name = 'CzbankWorker'
    bank_name = '浙商银行'
    begin_url = 'https://zp.czbank.com.cn/zpweb/planController/getPost.mvc?pageType=2&start=%s&end=6&depid=&educ=&orgId=&postName=&workYear=&location=&zpType=2&_=%s'
    headers = {'Referer': 'https://zp.czbank.com.cn/zpweb/planController/checkPage.mvc?pageType=2&postName='}
    page_size = 6

    async def start_manual(self):
        cookie_need = await fetch_bank_cookies(self.bank_name)
        headers = {'Cookie': cookie_need}
        for index in range(3):
            start = index * self.page_size
            random_time = int(time.time() * 1000)
            url = self.begin_url % (str(start), str(random_time))
            yield self.request(url=url, headers=headers, callback=self.parse, metadata={'Cookie': cookie_need})

    async def parse(self, response):
        cookie_need = response.metadata['Cookie']
        jsondata = await response.json()
        jsondata_need = jsondata['body'][0]
        async for item in CzbankItem.get_json(jsondata=jsondata_need):
            data = item.results
            headers = {'Cookie': cookie_need}
            target = Target(bank_name=self.bank_name, url=data['url'], headers=headers, metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # CzbankWorker.start()
    pass
