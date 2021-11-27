import weakref
from inspect import isawaitable
from config import Logger
from .exceptions import InvalidCallbackResult


class SpiderHook:
    """
    SpiderHook is used for extend spider
    """

    callback_result_map: dict = None
    logger = Logger(level='error').logger

    async def _run_spider_hook(self, hook_func):
        """
        Run hook before/after spider start crawling
        :param hook_func: aws function
        :return:
        """
        if callable(hook_func):
            try:
                aws_hook_func = hook_func(weakref.proxy(self))
                if isawaitable(aws_hook_func):
                    await aws_hook_func
            except Exception as e:
                self.logger.error(f"<Hook {hook_func.__name__}: {e}")

    async def process_failed_response(self, request, response):
        """
        Corresponding processing for the failed response
        :param request: Request
        :param response: Response
        :return:
        """
        pass

    async def process_succeed_response(self, request, response):
        """
        Corresponding processing for the succeed response
        :param request: Request
        :param response: Response
        :return:
        """
        pass

    async def process_item(self, item):
        """
        Corresponding processing for the Item type
        :param item: Item
        :return:
        """
        pass

    async def process_callback_result(self, callback_result):
        """
        Corresponding processing for the invalid callback result
        :param callback_result: Custom instance
        :return:
        """
        callback_result_name = type(callback_result).__name__
        process_func_name = self.callback_result_map.get(callback_result_name, "")
        process_func = getattr(self, process_func_name, None)
        if process_func is not None:
            await process_func(callback_result)
        else:
            raise InvalidCallbackResult(f"process_callback_result()方法中<Parse invalid callback result type: {callback_result_name}>")
