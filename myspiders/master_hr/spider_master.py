from myspiders.ruia import Master, Response, PyppeteerResponse
from urllib.parse import urlparse, urljoin
import re
import os
from bs4 import BeautifulSoup
import json
from copy import copy
from config import Target, CONFIG, Job
from constants import BankDict
from myspiders.spider_hr.icbc_spider import IcbcItem
from myspiders.spider_hr.ccb_spider import CcbItem
from myspiders.spider_hr.njcb_spider import NjcbItem
from myspiders.spider_hr.cscb_spider import CscbItem
from myspiders.spider_hr.szrcb_spider import SzrcbItem
import cchardet


class SpiderMaster(Master):
    name = 'SpiderMaster'
    url_num = CONFIG.MASTER_CRAWL_PER_TIME

    async def parse(self, response):
        target: Target = response.metadata['target']
        bank_name = target.bank_name
        if not target.callback:
            bank_alia = BankDict.list_bank_alia[bank_name]
            extract_method = getattr(self, 'extract_' + bank_alia, None)
        else:
            extract_method = getattr(self, target.callback, None)
        if extract_method is not None and callable(extract_method):
            yield extract_method(response, target)
        else:
            self.logger.error('【%s】没有找到相应的方法：extract_方法' % bank_name)

    async def extract_icbc(self, response: Response, target: Target):
        jsondata = await response.json()
        async for item in IcbcItem.get_json(jsondata=jsondata):
            data = item.results
            url_next = IcbcItem.url_next + data['job_id']
            target_next = Target(bank_name=target.bank_name, url=url_next, metadata={'data': data}, request_type='pyppeteer', callback='extract_icbc_next')
            await self.redis.insert(field=target_next.id, value=target_next.do_dump())

    async def extract_icbc_next(self, response: PyppeteerResponse, target: Target):
        data = target.metadata['data']
        html = response.html
        pattern = re.compile(r'<div class="editor-box.+?">(.+?)</div>')
        result = pattern.search(html)
        if result:
            content = result.group(1)
            chinese = re.compile(self.pattern_chinese).search(content)
            if chinese:
                data['content'] = content
                job = Job.do_load(data)
                await self.save_job(job=job, target=target)

    async def extract_ccb(self, response: Response, target: Target):
        jsondata = await response.json(content_type='text/html')
        async for item in CcbItem.get_json(jsondata=jsondata):
            data = item.results
            url_next = CcbItem.url_next_detail % (data['planId'], data['planPost'], data['planType'], data['orgId'], data['secondOrgId'])
            target_next = Target(bank_name=target.bank_name, url=url_next, request_type='splash', callback='extract_ccb_next', metadata={'data': data})
            await self.redis.insert(field=target_next.id, value=target_next.do_dump())

    async def extract_ccb_next(self, response: Response, target: Target):
        jsondata = await response.json()
        html = jsondata['html']
        data = target.metadata['data']
        soup = BeautifulSoup(html, 'lxml')
        requirement = soup.select_one('#asd .JDdown .JDD1')
        content = soup.select_one('#asd .JDdown .JDD2')
        data['content'] = content.get_text()
        data['requirement'] = requirement.get_text()
        data['url'] = response.url
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_cmbc(self, response: Response, target: Target):
        jsondata = await response.json()
        data = target.metadata['data']
        one = jsondata['data']
        if 'careerRecruitment_recruitingNumbers' in one.keys():
            data['recruit_num'] = one['careerRecruitment_recruitingNumbers']
        data['requirement'] = one['careerRecruitment_career_careerDetail_qualifications']
        data['content'] = one['careerRecruitment_career_careerDetail_content']
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)


    async def extract_cebbank(self, response: Response, target: Target):
        content = await response.read()
        encoding = cchardet.detect(content)['encoding']
        html = content.decode(encoding, errors='ignore')
        soup = BeautifulSoup(html, 'lxml')
        text = soup.select_one('#career_03 table').get_text(strip=True)
        data = target.metadata['data']
        data['content'] = text
        print('===========', data)
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_hxb(self, response: Response, target: Target):
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        data = target.metadata['data']
        body = soup.find(name='table', attrs={'class': 'table'})
        content = body.select_one('tr:nth-of-type(4) td:last-of-type').get_text(strip=True)
        requirement = body.select_one('tr:nth-of-type(5) td:last-of-type').get_text(strip=True)
        data['content'] = content
        data['requirement'] = requirement
        print('===========', data)
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_hfbank(self, response: Response, target: Target):
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        data = target.metadata['data']
        content = soup.select_one('#bg_grey div div.ypyq_contain div:nth-of-type(5)').get_text(strip=True)
        requirement = soup.select_one('#bg_grey div div.ypyq_contain div:nth-of-type(6)').get_text(strip=True)
        data['content'] = content
        data['requirement'] = requirement
        print('===========', data)
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_czbank(self, response: Response, target: Target):
        data = target.metadata['data']
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        branch_name = soup.select_one('div.barNav div.pull-left div p:nth-of-type(2) span:first-of-type')
        place = soup.select_one('div.barNav div.pull-left div p:nth-of-type(2) span:nth-of-type(2)')
        if branch_name:
            data['branch_name'] = branch_name.get_text(strip=True)
        if place:
            data['place'] = place.get_text(strip=True)

        data['content'] = ''
        content_part = soup.select_one('div.mainBody div.details:last-of-type')
        label_name = content_part.select_one('h2')
        if label_name:
            label_name_text = label_name.get_text(strip=True)
            if label_name_text == '职位描述':
                content = content_part.get_text(strip=True)
                data['content'] = content
        print('===========', data)
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_spdb(self, response: Response, target: Target):
        data = target.metadata['data']
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        content = soup.select_one('div.pf_common_row.pf_common_container div.pf_job_card2 p:nth-of-type(2)')
        requirement = soup.select_one('div.pf_common_row.pf_common_container div.pf_job_card2 p:last-of-type')
        if content:
            data['content'] = content.get_text(strip=True)
        if requirement:
            data['requirement'] = requirement.get_text(strip=True)
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)


    async def extract_bankofbeijing(self, response: Response, target: Target):
        data = target.metadata['data']
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        content = soup.select_one('.wrap .wrap_center ol:first-of-type')
        requirement = soup.select_one('.wrap .wrap_center ol:last-of-type')
        if content:
            data['content'] = content.get_text(strip=True)
        if requirement:
            data['requirement'] = requirement.get_text(strip=True)
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_njcb(self, response: Response, target: Target):
        jsondata = await response.json(content_type='text/html')
        async for item in NjcbItem.get_json(jsondata=jsondata):
            data = item.results
            url_next = NjcbItem.url_detail % (data['e01Id'], data['bm0000'], data['zpreqItemId'])
            target_next = Target(bank_name=target.bank_name, method='POST', url=url_next, metadata={'data': data}, callback='extract_njcb_next')
            await self.redis.insert(field=target_next.id, value=target_next.do_dump())

    async def extract_njcb_next(self, response: Response, target: Target):
        data = target.metadata['data']
        jsondata = await response.json(content_type='text/html')
        list_requirement = jsondata['obj']['gwrzList']
        list_content = jsondata['obj']['gwzzList']
        requirement = ''
        content = ''
        for one in list_requirement:
            text = one['rzDesc']
            requirement = requirement + text + '\n'
        for one in list_content:
            text = one['zzDesc']
            content = content + text + '\n'
        data['requirement'] = requirement
        data['content'] = content
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_nbcb(self, response: Response, target: Target):
        jsondata = await response.json()
        one = jsondata['data']
        data = {
            'bank_name': '宁波银行',
            'type_main': '社会招聘',
            'name': one['job'],
            'job_id': str(one['pid']),
            'branch_name': one['company'],
            'department': one['department'],
            'education': one['higlevel'],
            'recruit_num': str(one['reqnum']),
            'place': one['workcity'],
            'date_publish': one['pubtime'] + ' 00:00:00',
            'date_close': one['effecttime'] + ' 00:00:00',
            'requirement': one['jobrequire'],
            'content': one['duty'],
        }
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_bosc(self, response: Response, target: Target):
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        list_tr = soup.select('.bg .wrap .right .zwm table tr')
        for index in range(1, len(list_tr)):
            one = list_tr[index]
            data = {'bank_name': '上海银行', 'type_main': '社会招聘'}
            name_dom = one.select_one('td a')
            data['name'] = name_dom.get_text(strip=True)
            url = name_dom.get('href')
            if not url.startswith('http'):
                url = 'https://bosc.zhiye.com' + url
            data['url'] = url
            list_url = url.split('=')
            data['job_id'] = list_url[-1]
            data['branch_name'] = one.select_one('td:nth-of-type(2)').get_text(strip=True)
            data['place'] = one.select_one('td:nth-of-type(3)').get_text(strip=True)
            date = one.select_one('td:nth-of-type(4)').get_text(strip=True)
            data['date'] = date + ' 00:00:00'
            data['recruit_num'] = one.select_one('td:last-of-type').get_text(strip=True)
            target_next = Target(bank_name=target.bank_name, url=data['url'], metadata={'data': data}, callback='extract_bosc_next')
            await self.redis.insert(field=target_next.id, value=target_next.do_dump())

    async def extract_bosc_next(self, response: Response, target: Target):
        data = target.metadata['data']
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        content = soup.select_one('.bg .wrap .right div.zwxqm')
        if content:
            data['content'] = content.get_text()
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_suzhoubank(self, response: Response, target: Target):
        data = target.metadata['data']
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        list_tr = soup.select('table tr td table:nth-of-type(3) tr')
        for one in list_tr:
            label = one.select_one('td:first-of-type').get_text(strip=True)
            value = one.select_one('td:last-of-type').get_text()
            if label == '岗位职责':
                data['content'] = value
            if label == '任职条件':
                data['requirement'] = value
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_xacbank(self, response: Response, target: Target):
        data = target.metadata['data']
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        body = soup.select_one('.main .main_box div.position')
        education = body.select_one('.position_box .bd ul li:first-of-type span:last-of-type')
        if education:
            data['education'] = education.get_text(strip=True)
        content = body.select_one('div.position_box:nth-of-type(2) div.bd')
        if content:
            data['content'] = content.get_text()
        requirement = body.select_one('div.position_box:nth-of-type(3) div.bd')
        if requirement:
            data['requirement'] = requirement.get_text()
        job = Job.do_load(data)
        await self.save_job(job=job, target=target)

    async def extract_cscb(self, response: Response, target: Target):
        jsondata = await response.json(content_type='text/plain')
        async for item in CscbItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job, target=target)

    async def extract_szrcb(self, response: Response, target: Target):
        jsondata = await response.json(content_type='text/plain')
        async for item in SzrcbItem.get_json(jsondata=jsondata):
            data = item.results
            job = Job.do_load(data)
            await self.save_job(job=job, target=target)

    async def extract_zrcbank(self, response: Response, target: Target):
        data = target.metadata['data']
        html = await response.text()
        soup = BeautifulSoup(html, 'lxml')
        body = soup.select_one('.xiangqingcontain div.xiangqingtext')
        content = body.select_one('p:nth-of-type(2)')
        if content:
            data['content'] = content.get_text()
        requirement = body.select_one('p:last-of-type')
        if requirement:
            data['requirement'] = requirement.get_text()
        job = Job.do_load(data)
        await self.save_job(job, target=target)


def start():
    SpiderMaster.start()
