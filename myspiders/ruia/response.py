import json
from typing import Any, Callable, Optional
from http.cookies import SimpleCookie
from lxml import etree

DEFAULT_JSON_DECODER = json.loads
JSONDecoder = Callable[[str], Any]


class Response(object):
    """
    Return a friendly response
    """

    def __init__(
        self,
        url: str,
        method: str,
        *,
        encoding: str = "",
        html: str = "",
        metadata: dict,
        cookies,
        history,
        headers,
        formdata=None,
        status: int = -1,
        aws_json: Callable = None,
        aws_read: Callable = None,
        aws_text: Callable = None,
    ):
        self._callback_result = None
        self._encoding = encoding
        self._url = url
        self._method = method
        self._metadata = metadata
        self._html = html
        self._index = None
        self._cookies = cookies
        self._history = history
        self._headers = headers
        self._formdata = formdata
        self._status = status
        self._ok = self._status == 0 or 200 <= self._status <= 299

        self._aws_json = aws_json
        self._aws_read = aws_read
        self._aws_text = aws_text

    def __repr__(self):
        return f"<Response url[{self._method}]: {self._url} status:{self._status}>"

    @property
    def callback_result(self):
        return self._callback_result

    @callback_result.setter
    def callback_result(self, value):
        self._callback_result = value

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = value

    @property
    def ok(self) -> bool:
        return self._ok

    @ok.setter
    def ok(self, value: bool):
        self._ok = value

    @property
    def encoding(self):
        return self._encoding

    @property
    def url(self):
        return self._url

    @property
    def method(self):
        return self._method

    @property
    def metadata(self):
        return self._metadata

    @property
    def html(self):
        return self._html

    @property
    def cookies(self) -> dict:
        if isinstance(self._cookies, SimpleCookie):
            cur_cookies = {}
            for key, value in self._cookies.items():
                cur_cookies[key] = value.value
            return cur_cookies
        else:
            return self._cookies

    @property
    def history(self):
        return self._history

    @property
    def headers(self):
        return self._headers

    @property
    def formdata(self):
        return self._formdata

    @property
    def status(self):
        return self._status

    @property
    def html_etree(self):
        html_etree = None
        if self.html:
            html_etree = etree.HTML(self.html)
        return html_etree

    async def json(self, *, encoding: str = None, loads: JSONDecoder = DEFAULT_JSON_DECODER, content_type: Optional[str] = "application/json",) -> Any:
        """Read and decodes JSON response."""
        return await self._aws_json(encoding=encoding, loads=loads, content_type=content_type)

    async def read(self) -> bytes:
        """Read response payload."""
        return await self._aws_read()

    async def text(self, *, encoding: Optional[str] = None, errors: str = "strict") -> str:
        """Read response payload and decode."""
        return await self._aws_text(encoding=encoding, errors=errors)



class PyppeteerResponse(Response):

    def __init__(self, url: str, method: str, *,
                 encoding: str = '',
                 html: str = '',
                 page,
                 browser,
                 metadata: dict,
                 cookies,
                 history,
                 headers: dict = None,
                 status: int = -1,
                 aws_json: Callable = None,
                 aws_read: Callable = None,
                 aws_text: Callable = None):
        super(PyppeteerResponse, self).__init__(
            url=url,
            method=method,
            encoding=encoding,
            html=html,
            metadata=metadata,
            cookies=cookies,
            history=history,
            headers=headers,
            status=status,
            aws_json=aws_json,
            aws_read=aws_read,
            aws_text=aws_text
        )
        self._page = page
        self._browser = browser

    @property
    def page(self):
        return self._page

    @property
    def browser(self):
        return self._browser

    async def json(self, **kwargs):
        """Read and decodes JSON response."""
        return await self._aws_json(**kwargs)

    async def read(self, **kwargs):
        """Read response payload."""
        return await self._aws_read(**kwargs)

    async def text(self, **kwargs):
        """Read response payload and decode."""
        return await self._aws_text(**kwargs)

    def __str__(self):
        return f'<PyppeteerResponse url[{self._method}]: {self._url} status:{self._status}>'
