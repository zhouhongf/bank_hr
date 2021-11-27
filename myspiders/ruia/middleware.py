from collections import deque
from functools import wraps


class Middleware:
    """
    Define a middleware to customize the crawler request or response
    eg: middleware = Middleware()
    Middleware的目的是对每次请求前后进行一番处理，分下面两种情况：
    在每次请求之前做一些事 @middleware.request
    在每次请求后做一些事   @middleware.response
    """

    def __init__(self):
        # request middleware
        self.request_middleware = deque()
        # response middleware
        self.response_middleware = deque()

    def request(self, *args, **kwargs):
        """
        Define a Decorate to be called before a request.
        eg: @middleware.request
        """
        middleware = args[0]

        @wraps(middleware)
        def register_middleware(*args, **kwargs):
            self.request_middleware.append(middleware)
            return middleware

        return register_middleware()

    def response(self, *args, **kwargs):
        """
        Define a Decorate to be called after a response.
        eg: @middleware.response
        """
        middleware = args[0]

        @wraps(middleware)
        def register_middleware(*args, **kwargs):
            self.response_middleware.appendleft(middleware)
            return middleware

        return register_middleware()

    def __add__(self, other):
        new_middleware = Middleware()
        # asc
        new_middleware.request_middleware.extend(self.request_middleware)
        new_middleware.request_middleware.extend(other.request_middleware)
        # desc
        new_middleware.response_middleware.extend(other.response_middleware)
        new_middleware.response_middleware.extend(self.response_middleware)
        return new_middleware
