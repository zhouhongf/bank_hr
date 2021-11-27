from config import Target
from myspiders.ruia import JsonField, Item, Spider
import re
import farmhash
import time
from urllib.parse import urlencode, urlparse, urljoin, quote, unquote


'''
careerRecruitment_career_enterprise_name: "兰州分行"
careerRecruitment_career_expirationDate: "2020-06-30"
careerRecruitment_career_jobFamily_name: "业务经营"
careerRecruitment_career_name: "零售支行行长"
careerRecruitment_career_publishDate: "2020-01-21 11:10:38"
careerRecruitment_regions_name: "兰州"
id: "c0237853-3b65-4175-9243-8d9e7fe5bc6b"
'''
class CmbcItem(Item):
    url_detail = 'http://career.cmbc.com.cn:8080/index.jsp?_rd=%s#/app/recruitmentview/%s'
    url_next = 'http://career.cmbc.com.cn:8080/portal/rest/careerrecruitment/view/%s.view?random=%s&view=careerRecruitmentView&recruitmentId=%s'

    target_item = JsonField(json_select='data>items')

    bank_name = JsonField(default='民生银行')
    type_main = JsonField(default='社会招聘')

    name = JsonField(json_select='careerRecruitment_career_name')
    job_id = JsonField(json_select='id')
    branch_name = JsonField(json_select='careerRecruitment_career_enterprise_name')
    department = JsonField(json_select='careerRecruitment_career_jobFamily_name')

    place = JsonField(json_select='careerRecruitment_regions_name')
    date_publish = JsonField(json_select='careerRecruitment_career_publishDate')
    date_close = JsonField(json_select='careerRecruitment_career_expirationDate')

    async def clean_date_close(self, value):
        return value + ' 00:00:00'


# 因为有重复变量，所以加在一起
def make_form_data(page_count: int, page_size: int):
    formdata_list = []
    for index in range(page_count):
        formdata = {
            'view': 'careerRecruitmentList',
            'pageNo': index + 1,
            'pageSize': page_size,
            'sortField': 'careerRecruitment_career_publishDate',
            'sortOrder': 'desc',
            'searchRecruitmentIds': 'social',
        }
        one = urlencode(formdata) + '&searchRecruitmentIds=advanced'
        formdata_list.append(one)
    return formdata_list


# 先抓取全部理财产品的code, 再分别查询MongoDB数据库中的outline和manual, 如没有，则下载
class CmbcWorker(Spider):
    name = 'CmbcWorker'
    bank_name = '民生银行'
    begin_url = 'http://career.cmbc.com.cn:8080/portal/rest/careerrecruitment/search.view?random='
    page_size = 20

    async def start_manual(self):
        form_data = make_form_data(10, self.page_size)
        for formdata in form_data:
            random_time = int(time.time() * 1000) + 10 * 60 * 60 * 1000
            time.sleep(2)
            url = self.begin_url + str(random_time)
            url_full = url + '&' + formdata
            yield self.request(url=url_full, method='POST', callback=self.parse)

    async def parse(self, response):
        jsondata = await response.json()
        async for item in CmbcItem.get_json(jsondata=jsondata):
            data = item.results
            random_time = int(time.time() * 1000) + 10 * 60 * 60 * 1000
            job_id = data['job_id']
            data['url'] = CmbcItem.url_detail % (random_time, job_id)
            url_next = CmbcItem.url_next % (job_id, random_time, job_id)
            target = Target(bank_name=self.bank_name, url=url_next, metadata={'data': data})
            await self.redis.insert(field=target.id, value=target.do_dump())


def start():
    # CmbcWorker.start()
    pass
