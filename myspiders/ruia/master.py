import asyncio
import typing
from signal import SIGINT, SIGTERM
from datetime import datetime
from types import AsyncGeneratorType
from aiohttp import ClientSession
from database.bankends import MongoDatabase, RedisDatabase
from .exceptions import (
    NotImplementedParseError,
    NothingMatchedError,
)
from .item import Item
from .request import Request
from .response import Response
from .hooker import SpiderHook
from config import Target, SpiderCount, Job


try:
    import uvloop
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
except ImportError:
    pass


class Master(SpiderHook):
    name = None
    url_num: int = 3
    request_config = None

    headers: dict = None
    metadata: dict = None
    kwargs: dict = None

    failed_counts: int = 0
    success_counts: int = 0
    worker_numbers: int = 2
    concurrency: int = 3
    worker_tasks: list = []

    pattern_link = r'http[s]?://[0-9a-zA-Z/\?=&\.]+'
    pattern_date = '20[0-9]{2}[-年/][01]?[0-9][-月/][0123]?[0-9]日?'
    pattern_date_extra = r'20\.\d{2}\.\d{2}'
    pattern_chinese = r'[\u4e00-\u9fa5]'
    pattern_number = r'\d'
    pattern_letter = r'[a-zA-Z]'

    def __init__(
            self,
            name=None,
            start_urls: list = None,
            loop=None,
            is_async_start: bool = False,
            cancel_tasks: bool = True,
            **kwargs,
    ):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)

        if not isinstance(self.url_num, int):
            raise ValueError("url_num must be type of int")

        self.start_urls = start_urls or []
        if not isinstance(self.start_urls, typing.Iterable):
            raise ValueError("start_urls must be Iterable")

        self.loop = loop
        asyncio.set_event_loop(self.loop)
        self.request_queue = asyncio.Queue()
        self.sem = asyncio.Semaphore(self.concurrency)
        # Init object-level properties  SpiderHook的类属性
        self.callback_result_map = self.callback_result_map or {}

        self.headers = self.headers or {}
        self.metadata = self.metadata or {}
        self.kwargs = self.kwargs or {}
        self.request_config = self.request_config or {}
        self.request_session = ClientSession()
        self.cancel_tasks = cancel_tasks
        self.is_async_start = is_async_start

        # Mongo数据库
        self.mongo = MongoDatabase()
        mongo_db = self.mongo.db()
        self.collection_job = mongo_db['JOB']
        self.collection_spider_count = mongo_db['spider_count']

        # Redis数据库用于临时储存待爬取的link对象
        self.redis = RedisDatabase()

    async def _start(self, after_start=None, before_stop=None):
        print('【=======================================启动：%s=========================================】' % self.name)
        start_time = datetime.now()

        for signal in (SIGINT, SIGTERM):
            try:
                self.loop.add_signal_handler(signal, lambda: asyncio.ensure_future(self.stop(signal)))
            except NotImplementedError:
                pass

        try:
            await self._run_spider_hook(after_start)
            await self.start_master()
            await self._run_spider_hook(before_stop)
        finally:
            await self.request_session.close()

            end_time = datetime.now()
            spider_count = SpiderCount(name=self.name, time_start=start_time, time_end=end_time, success=self.success_counts, failure=self.failed_counts)
            self.collection_spider_count.insert_one(spider_count.do_dump())
            print(spider_count)
            print('----------- 用时：%s ------------' % (end_time - start_time))


    @classmethod
    async def async_start(cls, start_urls: list = None, loop=None, after_start=None, before_stop=None, cancel_tasks: bool = True, **kwargs):
        loop = loop or asyncio.get_event_loop()
        spider_ins = cls(start_urls=start_urls, loop=loop, is_async_start=True, cancel_tasks=cancel_tasks, **kwargs)
        await spider_ins._start(after_start=after_start, before_stop=before_stop)
        return spider_ins

    @classmethod
    def start(cls, start_urls: list = None, loop=None, after_start=None, before_stop=None, close_event_loop=True, **kwargs):
        print('【=======================================启动：%s=========================================】' % cls.name)
        loop = loop or asyncio.new_event_loop()
        spider_ins = cls(start_urls=start_urls, loop=loop, **kwargs)
        spider_ins.loop.run_until_complete(spider_ins._start(after_start=after_start, before_stop=before_stop))
        spider_ins.loop.run_until_complete(spider_ins.loop.shutdown_asyncgens())
        if close_event_loop:
            spider_ins.loop.close()
        return spider_ins

    async def start_master(self):
        async for request_ins in self.process_start_urls():
            self.request_queue.put_nowait(self.handle_request(request_ins))

        workers = [asyncio.ensure_future(self.start_worker()) for i in range(self.worker_numbers)]
        for worker in workers:
            self.logger.info(f"Worker started ================= ID: {id(worker)}")
        await self.request_queue.join()      # 阻塞至队列中所有的元素都被接收和处理完毕。当未完成计数降到零的时候， join() 阻塞被解除。

        if not self.is_async_start:          # 如果不是is_async_start，即不是异步启动的，则等待执行stop()方法
            await self.stop(SIGINT)
        else:
            if self.cancel_tasks:            # 如果是异步启动的，在async_start()方法中，实例化Spider类时定义cancel_tasks为True, 则，取消前面的tasks, 执行当前异步启动的task
                await self._cancel_tasks()

    async def start_worker(self):
        while True:
            request_item = await self.request_queue.get()
            self.worker_tasks.append(request_item)
            if self.request_queue.empty():
                results = await asyncio.gather(*self.worker_tasks, return_exceptions=True)
                for task_result in results:
                    if not isinstance(task_result, RuntimeError) and task_result:
                        callback_results, response = task_result
                        if isinstance(callback_results, AsyncGeneratorType):
                            await self._process_async_callback(callback_results, response)
                self.worker_tasks = []
            self.request_queue.task_done()    # 每当消费协程调用 task_done() 表示这个条目item已经被回收，该条目所有工作已经完成，未完成计数就会减少。

    # 【仅仅改写的process_start_urls方法的内容，将spider开始爬取的目标，使用target类，可以自由定制】
    async def process_start_urls(self):
        targets = await self.redis.get_randoms(num=self.url_num)
        for one in targets:
            target = Target.do_load(one)
            await self.cleanup_target_db(target)  # 每次请求，即清洗一遍该target, 同样的target，超过5次，就自动删除
            print('Master的target内容：', target)
            yield self.request(
                url=target.url,
                method=target.method,
                headers=target.headers,
                formdata=target.formdata,
                formdata_type=target.formdata_type,
                request_type=target.request_type,
                callback=self.parse,
                metadata={'target': target}
            )

    async def cleanup_target_db(self, target: Target):
        fails = int(target.fails)
        if fails < 5:
            fails += 1
            target.fails = fails
            await self.redis.update_one(field=target.id, value=target.do_dump())
        else:
            await self.redis.delete_one(field=target.id)

    def request(
            self,
            url: str = 'http://httpbin.org/get',
            method: str = "GET",
            *,
            callback=None,
            encoding: typing.Optional[str] = None,
            headers: dict = None,
            formdata: dict = None,
            formdata_type: str = 'data',
            metadata: dict = None,
            request_config: dict = None,
            request_session=None,
            request_type: str = 'aiohttp',
            **kwargs,
    ):
        headers = headers or {}
        formdata = formdata or {}
        formdata_type = formdata_type
        metadata = metadata or {}
        request_config = request_config or {}
        request_session = request_session or self.request_session
        request_type = request_type

        headers.update(self.headers.copy())
        request_config.update(self.request_config.copy())
        kwargs.update(self.kwargs.copy())

        if formdata:
            method = 'POST'
        return Request(
            url=url,
            method=method,
            callback=callback,
            encoding=encoding,
            headers=headers,
            formdata=formdata,
            formdata_type=formdata_type,
            metadata=metadata,
            request_config=request_config,
            request_session=request_session,
            request_type=request_type,
            **kwargs,
        )

    async def parse(self, response):
        raise NotImplementedParseError("<!!! parse function is expected !!!>")

    async def handle_request(self, request: Request) -> typing.Tuple[AsyncGeneratorType, Response]:
        callback_result, response = None, None
        try:
            callback_result, response = await request.fetch_callback(self.sem)
            await self._process_response(request=request, response=response)
        except NotImplementedParseError as e:
            self.logger.error(e)
        except NothingMatchedError as e:
            error_info = f"<Field: {str(e).lower()}" + f", error url: {request.url}>"
            self.logger.error(error_info)
        except Exception as e:
            self.logger.error(f"<Callback[{request.callback.__name__}]: {e}")
        return callback_result, response

    async def handle_callback(self, aws_callback: typing.Coroutine, response):
        """Process coroutine callback function"""
        callback_result = None
        try:
            callback_result = await aws_callback
        except NothingMatchedError as e:
            self.logger.error(f"<Item: {str(e).lower()}>")
        except Exception as e:
            self.logger.error(f"<Callback[{aws_callback.__name__}]: {e}")
        return callback_result, response

    # 重要！处理异步回调函数的方法，在start_worker()方法中，启动该方法
    # 从返回结果callback_results中迭代每一个返回结果callback_result, 根据其不同的类别，套用不同的执行方法
    async def _process_async_callback(self, callback_results: AsyncGeneratorType, response: Response = None):
        try:
            async for callback_result in callback_results:
                if isinstance(callback_result, AsyncGeneratorType):
                    await self._process_async_callback(callback_result)
                elif isinstance(callback_result, Request):
                    self.request_queue.put_nowait(self.handle_request(request=callback_result))
                elif isinstance(callback_result, typing.Coroutine):
                    self.request_queue.put_nowait(self.handle_callback(aws_callback=callback_result, response=response))
                elif isinstance(callback_result, Item):
                    await self.process_item(callback_result)
                else:
                    await self.process_callback_result(callback_result=callback_result)
        except NothingMatchedError as e:
            error_info = f"<Field: {str(e).lower()}" + f", error url: {response.url}>"
            self.logger.error(error_info)
        except Exception as e:
            self.logger.error(f'_process_async_callback方法显示：{e}')

    async def _process_response(self, request: Request, response: Response):
        if response:
            if response.ok:
                await self.process_succeed_response(request, response)
            else:
                await self.process_failed_response(request, response)

    async def process_succeed_response(self, request, response):
        self.success_counts += 1

    async def process_failed_response(self, request, response):
        self.failed_counts += 1

    async def stop(self, _signal):
        await self._cancel_tasks()
        self.loop.stop()

    async def _cancel_tasks(self):
        tasks = []
        for task in asyncio.Task.all_tasks():
            if task is not asyncio.tasks.Task.current_task():
                tasks.append(task)
                task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

    async def save_job(self, job: Job, target: Target):
        data = job.do_dump()
        print('========== 准备保存job: ', data)
        self.mongo.do_insert_one(self.collection_job, {'_id': data['_id']}, data)
        await self.redis.delete_one(field=target.id)





