from myspiders.ruia.middleware import Middleware


middleware2 = Middleware()


@middleware2.request
async def print_on_request(spider_ins, request):
    request.metadata = {"url": request.url}
    print(f"在middleware2中请求的request: {request.metadata}")
    # Just operate request object, and do not return anything.


@middleware2.response
async def print_on_response(spider_ins, request, response):
    print(f"在middleware2中返回的response: {response.status}")
