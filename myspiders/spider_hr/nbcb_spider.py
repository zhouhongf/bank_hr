from myspiders.ruia import Item, Spider, Bs4HtmlField, Bs4AttrField, Bs4TextField, JsonField, RegexField
from urllib.parse import urlencode, urlparse, urljoin, quote
from config import Target, CONFIG
import re
import math
from bs4 import BeautifulSoup
import time
import random

'''
CompID: 447
PubTime: "2020-05-29 11:03:00.0"
company: "衢州分行"
compl: "衢州分行"
department: "衢州分行零售公司二部"
effecttime: "2020-06-30"
job: "零售公司二部总经理"
orderType: 1
pid: 7109
reqnum: 1
workcity: "衢州"
yjdep: 146
'''

'''
boardline: "零售公司业务"
company: "衢州分行"
compdetails: "无"
department: "衢州分行零售公司二部"
duty: "根据零售公司（中小企业）条线发展目标，推动小微贷业务开拓，确保零售业务有序开展；负责组织营销活动，不断拓展客户群体，带领部门员工完成各项经营目标。"
effecttime: "2020-06-30"
higlevel: "本科及以上"
isKJJob: null
job: "零售公司二部总经理"
jobrequire: "1、40周岁及以下，全日制本科及以上学历；↵2、5年以上银行工作经历，熟悉小企业业务产品和本地市场情况。"
pid: 7109
pubtime: "2020-05-29"
reqnum: 1
workcity: "衢州"
workyears: "5年以上"
'''

class NbcbItem(Item):
    target_item = JsonField(json_select='data')

    bank_name = JsonField(default='宁波银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='job')
    job_id = JsonField(json_select='pid')
    branch_name = JsonField(json_select='company')
    department = JsonField(json_select='department')

    education = JsonField(json_select='higlevel')

    recruit_num = JsonField(json_select='reqnum')
    place = JsonField(json_select='workcity')
    date_publish = JsonField(json_select='pubtime')
    date_close = JsonField(json_select='effecttime')

    requirement = JsonField(json_select='jobrequire')
    content = JsonField(json_select='duty')

    async def clean_job_id(self, value):
        return str(value)

    async def clean_date_publish(self, value):
        return value + ' 00:00:00'

    async def clean_date_close(self, value):
        return value + ' 00:00:00'

    async def clean_recruit_num(self, value):
        if not value:
            return ''
        return str(value)


splash_url = 'http://%s:8050/execute?lua_source=' % CONFIG.HOST_LOCAL
lua_script = '''
function process_one(splash)
    splash:runjs("$('#pageDiv > a.next').click()")
    splash:wait(2)
    splash:set_viewport_full()
    assert(splash:wait(1))
    
    local current_page = splash:evaljs("$('#jobTable').html()")
    return {html = current_page}
end
function process_mul(splash,totalPageNum)
    local res={}
    for i=2,totalPageNum,1 do
        res[i]=process_one(splash)
    end
    return res
end
function main(splash, args)
    splash.resource_timeout = 1800
    splash.indexeddb_enabled = true

    local myheaders = {}
    myheaders['User-Agent']='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    assert(splash:go{'%s', headers=myheaders})
    assert(splash:wait(2))
    splash:set_viewport_full()
    assert(splash:wait(1))

    local current_page = splash:evaljs("$('#jobTable').html()")
    local page_total = splash:evaljs("$('#pageDiv span').html()")
    
    local results={}
    results = process_mul(splash, 3)
    results[1] = {html = current_page}

    return {
        results = results,
        page_total = page_total,
    }
end'''



# 爬取前3页页面
class NbcbWorker(Spider):
    name = 'NbcbWorker'
    bank_name = '宁波银行'
    begin_url = 'https://zhaopin.nbcb.com.cn/recruit/com.nbcb.recruit.social.socialMain.flow'
    url_detail = 'https://zhaopin.nbcb.com.cn/recruit/com.nbcb.recruit.comm.jobManager.getJobDetail.biz.ext?pid=%s&_=%s'

    async def start_manual(self):
        lua = lua_script % self.begin_url
        url = splash_url + quote(lua)
        yield self.request(url=url, callback=self.parse)

    async def parse(self, response):
        jsondata = await response.json()
        results = jsondata['results']
        list_pid = []
        for index in range(1, len(results) + 1):
            one = results[str(index)]
            html = one['html']
            soup = BeautifulSoup(html, 'lxml')
            list_input = soup.select('tr td:last-of-type input')
            for two in list_input:
                pid = two.get('value')
                list_pid.append(pid)

        for pid in list_pid:
            time_need = int(time.time() * 1000)
            url_next = self.url_detail % (pid, str(time_need))
            headers = {'Referer': 'https://zhaopin.nbcb.com.cn/recruit/com.nbcb.recruit.social.socialMain.flow'}
            target = Target(bank_name=self.bank_name, headers=headers, url=url_next)
            await self.redis.insert(field=target.id, value=target.do_dump())

        print('宁波银行================list_pid总共有：', list_pid)


def start():
    # NbcbWorker.start()
    pass
