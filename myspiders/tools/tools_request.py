import asyncio
import aiofiles
import aiohttp
import async_timeout
import os
import random
import requests
from collections import namedtuple
import pyppeteer
import tkinter


try:
    from ujson import loads as json_loads
except:
    from json import loads as json_loads


url_httpbin_get = 'http://httpbin.org/get'


def get_ip():
    try:
        r = requests.get(url_httpbin_get, timeout=10)
        jsondata = r.json()
        ip = jsondata['origin'].split(',')[0]
    except:
        ip = '0.0.0.0'
    return ip


async def fetch(client, url, proxy=None, params=None, timeout=15):
    if params is None:
        params = {}
    with async_timeout.timeout(timeout):
        try:
            headers = {'user-agent': await get_random_user_agent()}
            async with client.get(url, headers=headers, proxy=proxy, params=params, timeout=timeout) as response:
                assert response.status == 200
                try:
                    text = await response.text()
                except:
                    text = await response.read()
                return text
        except Exception as e:
            return None


async def request_html_by_aiohttp(url, proxy=None, params=None, timeout=15):
    if params is None:
        params = {}
    async with aiohttp.ClientSession() as client:
        html = await fetch(client=client, url=url, proxy=proxy, params=params, timeout=timeout)
        return html if html else None


def request_html_by_requests(url, proxies):
    """
    Request a url by requests
    :param url:
    :param proxies:
    :return:
    """
    headers = {
        'User-Agent': get_random_user_agent()
    }
    try:
        res = requests.get(url, headers=headers, timeout=10, proxies=proxies)
        res.raise_for_status()
    except requests.exceptions.ConnectTimeout as e:
        res = None
    except Exception as e:
        res = None
    return res


async def get_proxy_info(ip, port, get_info=False):
    proxies = {
        "http": "http://{ip}:{port}".format(ip=ip, port=port),
        "https": "http://{ip}:{port}".format(ip=ip, port=port)
    }
    is_ok, info = await valid_proxies(ip, port)
    if get_info:
        return is_ok, info
    else:
        return is_ok


async def valid_proxies(ip, port):
    """
    Return all usable proxies without socket 4/5
    :param ip:
    :param port:
    :return:
    """
    # TODO valid socket 4/5
    # response = request_url_by_requests(url=CONFIG.TEST_URL['http'], proxies=proxies)
    proxy = "http://{ip}:{port}".format(ip=ip, port=port)
    html = await request_html_by_aiohttp(url='http://httpbin.org/get', proxy=proxy, timeout=10)
    if html:
        try:
            res_json = json_loads(html)
            headers = res_json.get('headers', {})
            X_Forwarded_For = headers.get('X-Forwarded-For')
            Proxy_Connection = headers.get('Proxy-Connection')
            if X_Forwarded_For and ',' in X_Forwarded_For:
                types = 3
            elif Proxy_Connection:
                types = 2
            else:
                types = 1
            info = {
                'proxy': "{ip}:{port}".format(ip=ip, port=port),
                'types': types
            }
            return True, info
        except Exception as e:
            return False, None
    else:
        return False, None


async def get_random_user_agent():
    """
    Get a random user agent string.
    :return: Random user agent string.
    """
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
    return random.choice(await _get_data('user_agents.txt', USER_AGENT))


async def _get_data(filename, default=''):
    """
    Get audit from a file
    :param filename: filename
    :param default: default value
    :return: audit
    """
    root_folder = os.path.dirname(__file__)
    user_agents_file = os.path.join(root_folder, filename)
    try:
        async with aiofiles.open(user_agents_file, mode='r') as f:
            data = [_.strip() for _ in await f.readlines()]
    except:
        data = [default]
    return data


"""使用tkinter获取屏幕大小"""
def screen_size():
    tk = tkinter.Tk()
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    return width, height


Response = namedtuple("rs", "title url html cookies headers history status metadata")


async def get_html_pypeteer(url, cookies=None, metadata=None, timeout=30):
    if metadata is None:
        metadata = {}
    browser = await pyppeteer.launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setJavaScriptEnabled(enabled=True)
    await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36')
    if cookies:
        await page.setCookie(cookies)
    width, height = screen_size()
    await page.setViewport(viewport={"width": width, "height": height})
    res = await page.goto(url, options={'timeout': int(timeout * 1000)})
    data = await page.content()
    title = await page.title()
    resp_cookies = await page.cookies()
    resp_headers = res.headers
    resp_history = None
    resp_status = res.status
    await browser.close()

    response = Response(title=title, url=url, html=data, cookies=resp_cookies, headers=resp_headers, history=resp_history, status=resp_status, metadata=metadata)
    return response


if __name__ == '__main__':
    ip, port = '182.45.176.77', 6666
    proxies = {
        "http": "http://{ip}:{port}".format(ip=ip, port=port),
        "https": "https://{ip}:{port}".format(ip=ip, port=port)
    }

    proxy = "http://{ip}:{port}".format(ip=ip, port=port)

    print(asyncio.get_event_loop().run_until_complete(get_random_user_agent()))

    print(asyncio.get_event_loop().run_until_complete(get_proxy_info(ip, port, get_info=True)))
