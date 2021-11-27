from myspiders.tools.tools_request import get_random_user_agent
from myspiders.ruia.middleware import Middleware


middleware = Middleware()


@middleware.request
async def add_random_ua(spider_ins, request):
    ua = await get_random_user_agent()
    if request.headers:
        request.headers.update({'User-Agent': ua})
    else:
        request.headers = {'User-Agent': ua}
    # print('【ua_random获取request方法是：%s, form_data是：%s】' % (request.method, request.form_data))


@middleware.response
async def print_on_response(spider_ins, request, response):
    # print(f"【ua_random中返回的response: {response.status}】")
    pass
