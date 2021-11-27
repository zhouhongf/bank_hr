#!/usr/bin/env python
# Request类中，通过构造方法实例化后，添加了form_data的实例属性, 用来实现Spider的POST请求
import asyncio
import weakref
import aiohttp
import async_timeout
from inspect import iscoroutinefunction
from types import AsyncGeneratorType
from typing import Coroutine, Optional, Tuple
from asyncio.locks import Semaphore
from urllib.parse import quote
try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass

from .exceptions import InvalidRequestMethod
from .response import Response, PyppeteerResponse
from config import Logger, CONFIG
from myspiders.tools.tools_request import get_random_user_agent
import pyppeteer
import tkinter


splash_url = 'http://%s:8050/execute?lua_source=' % CONFIG.HOST_LOCAL
lua_script = '''
function main(splash, args)
    local myheaders = {}
    myheaders['User-Agent']='%s'
    assert(splash:go{'%s', headers=myheaders})
    assert(splash:wait(2))
    return {
        html = splash:html(),
        cookies = splash:get_cookies(),
    }
end'''


def screen_size():
    tk = tkinter.Tk()
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    return width, height


class Request(object):
    """
    Request class for each request
    Request的主要作用是方便地处理网络请求，最终返回一个Response对象。
    主要提供的方法有：
    Request().fetch：请求一个网页资源，可以单独使用
    Request().fetch_callback：为Spider类提供的和核心方法
    """

    name = "Request"

    # Default config
    REQUEST_CONFIG = {
        "RETRIES": 3,
        "DELAY": 0,
        "RETRY_DELAY": 0,
        "TIMEOUT": 10,
        "RETRY_FUNC": Coroutine,
        "VALID": Coroutine,
    }

    METHOD = ["GET", "POST"]

    def __init__(
        self,
        url: str,
        method: str = "GET",
        *,
        callback=None,
        encoding: Optional[str] = None,
        headers: dict = None,
        formdata: dict = None,
        formdata_type: str = None,
        metadata: dict = None,
        request_type: str = None,
        request_config: dict = None,
        request_session=None,
        **aiohttp_kwargs,
    ):
        """
        Initialization parameters
        :param url: Target url
        :param method: HTTP method
        :param callback: Callback func
        :param encoding: Html encoding
        :param headers: Request headers
        :param metadata: Send the audit to callback func
        :param request_config: Manage the target request
        :param request_session: aiohttp.ClientSession
        :param aiohttp_kwargs:
        """
        self.url = url
        self.method = method.upper()

        if self.method not in self.METHOD:
            raise InvalidRequestMethod(f"{self.method} method is not supported")

        self.callback = callback
        self.encoding = encoding
        self.headers = headers or {}
        self.formdata = formdata or {}
        self.formdata_type = formdata_type or 'data'
        self.metadata = metadata or {}
        self.request_type = request_type or 'aiohttp'
        self.request_config = (
            self.REQUEST_CONFIG if request_config is None else request_config
        )
        self.request_session = request_session
        # 自己增加的属性，用于传递POST请求的form_data参数

        self.ssl = aiohttp_kwargs.pop("ssl", False)
        self.aiohttp_kwargs = aiohttp_kwargs

        self.close_request_session = False
        self.logger = Logger(level='warning').logger
        self.retry_times = self.request_config.get("RETRIES", 3)

    def __repr__(self):
        return f"<{self.method} {self.url}>"

    @property
    def current_request_session(self):
        if self.request_session is None:
            self.request_session = aiohttp.ClientSession()
            self.close_request_session = True
        return self.request_session

    async def fetch(self, delay=True) -> Response:
        if delay and self.request_config.get("DELAY", 0) > 0:
            await asyncio.sleep(self.request_config["DELAY"])
        try:
            response = await self._make_request()
            # Retry middleware
            aws_valid_response = self.request_config.get("VALID")
            if aws_valid_response and iscoroutinefunction(aws_valid_response):
                response = await aws_valid_response(response)
            if response.ok:
                return response
            else:
                return await self._retry(error_msg=f"Request url failed with status {response.status}!")
        except asyncio.TimeoutError:
            return await self._retry(error_msg="timeout")
        except Exception as e:
            return await self._retry(error_msg=e)
        finally:
            # Close client session
            await self._close_request()

    async def fetch_callback(self, sem: Semaphore) -> Tuple[AsyncGeneratorType, Response]:
        """
        Request the target url and then call the callback function
        :param sem: Semaphore
        :return: Tuple[AsyncGeneratorType, Response]
        """
        try:
            async with sem:
                response = await self.fetch()
        except Exception as e:
            response = None
            self.logger.error(f"<Error: {self.url} {e}>")

        if self.callback is not None:
            if iscoroutinefunction(self.callback):
                callback_result = await self.callback(response)
            else:
                callback_result = self.callback(response)
        else:
            callback_result = None
        # response.callback_result = callback_result
        return callback_result, response

    async def _close_request(self):
        if self.close_request_session:
            await self.request_session.close()

    # ！！用于真正的发起request请求
    async def _make_request(self):
        # self.logger.info(f"<{self.method}: {self.url}>")
        print('method, url, headers', self.method, self.url, self.headers)
        if self.request_type == 'pyppeteer':
            resp = await self._make_request_by_pyppeteer()
        elif self.request_type == 'splash':
            resp = await self._make_request_by_splash()
        else:
            resp = await self._make_request_by_aiohttp()
        return resp

    async def _make_request_by_aiohttp(self):
        timeout = self.request_config.get("TIMEOUT", 10)
        async with async_timeout.timeout(timeout):
            user_agent = await get_random_user_agent()
            self.headers.update({'User-Agent': user_agent})
            if self.method == "GET":
                request_func = self.current_request_session.get(self.url, headers=self.headers, ssl=self.ssl, **self.aiohttp_kwargs)
            else:
                if self.formdata_type == 'data':
                    request_func = self.current_request_session.post(self.url, headers=self.headers, ssl=self.ssl, data=self.formdata, **self.aiohttp_kwargs)
                else:
                    request_func = self.current_request_session.post(self.url, headers=self.headers, ssl=self.ssl, json=self.formdata, **self.aiohttp_kwargs)
            resp = await request_func
        try:
            resp_data = await resp.text(encoding=self.encoding)
        except UnicodeDecodeError:
            resp_data = await resp.read()

        response = Response(
            url=self.url,
            method=self.method,
            encoding=resp.get_encoding(),
            html=resp_data,
            metadata=self.metadata,
            cookies=resp.cookies,
            headers=resp.headers,
            formdata=self.formdata,
            history=resp.history,
            status=resp.status,
            aws_json=resp.json,
            aws_text=resp.text,
            aws_read=resp.read,
        )
        return response

    async def _make_request_by_splash(self):
        print('==================== 使用_make_request_by_splash请求：', self.url)
        timeout = self.request_config.get("TIMEOUT", 10)
        async with async_timeout.timeout(timeout):
            user_agent = await get_random_user_agent()
            lua = lua_script % (user_agent, self.url)
            url = splash_url + quote(lua)
            request_func = self.current_request_session.get(url=url, headers=self.headers, ssl=self.ssl, **self.aiohttp_kwargs)
            resp = await request_func

        resp_data = await resp.json()
        cookies = resp_data['cookies']
        html = resp_data['html']

        response = Response(
            url=self.url,
            method=self.method,
            encoding=resp.get_encoding(),
            html=html,
            metadata=self.metadata,
            cookies=cookies,
            headers=self.headers,
            formdata=self.formdata,
            history=None,
            status=resp.status,
            aws_json=resp.json,
            aws_text=resp.text,
            aws_read=resp.read,
        )
        return response


    async def _make_request_by_pyppeteer(self):
        print('==================== 使用_make_request_by_pypeteer请求：', self.url)
        timeout = self.request_config.get("TIMEOUT", 10)
        user_agent = await get_random_user_agent()
        browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'])

        page = await browser.newPage()
        await page.setJavaScriptEnabled(enabled=True)
        await page.setUserAgent(userAgent=user_agent)
        resp = await page.goto(url=self.url, options={'timeout': int(timeout * 2000)})
        width, height = screen_size()
        await page.setViewport(viewport={"width": width, "height": height})

        html = await page.content()
        title = await page.title()
        resp_cookies = await page.cookies()
        await browser.close()

        response = PyppeteerResponse(url=self.url,
                                     method=self.method,
                                     encoding=self.encoding,
                                     html=html,
                                     page=page,
                                     browser=browser,
                                     metadata=self.metadata,
                                     cookies=resp_cookies,
                                     headers=resp.headers,
                                     history=(),
                                     status=resp.status,
                                     aws_json=resp.json,
                                     aws_text=resp.text,
                                     aws_read=resp.buffer)
        return response

    async def _retry(self, error_msg):
        """Manage request"""
        if self.retry_times > 0:
            # Sleep to give server a chance to process/cache prior request
            if self.request_config.get("RETRY_DELAY", 0) > 0:
                await asyncio.sleep(self.request_config["RETRY_DELAY"])

            retry_times = self.request_config.get("RETRIES", 3) - self.retry_times + 1
            self.logger.error(f"<Retry url: {self.url}>, Retry times: {retry_times}, Retry message: {error_msg}>")
            self.retry_times -= 1
            retry_func = self.request_config.get("RETRY_FUNC")
            if retry_func and iscoroutinefunction(retry_func):
                request_ins = await retry_func(weakref.proxy(self))
                if isinstance(request_ins, Request):
                    return await request_ins.fetch()
            return await self.fetch()
        else:
            response = Response(
                url=self.url,
                method=self.method,
                metadata=self.metadata,
                cookies={},
                history=(),
                headers=None,
                formdata=self.formdata
            )

            return response

