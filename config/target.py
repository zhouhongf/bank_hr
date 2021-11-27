import time
import farmhash


# type_main用于选择执行请求的方式：aiohttp, splash, selenium, py
class Target:

    def __init__(
            self,
            bank_name: str = None,
            url: str = 'http://httpbin.org/get',
            method: str = 'GET',
            headers: dict = None,
            request_type: str = 'aiohttp',
            formdata: dict = None,
            formdata_type: str = 'data',
            callback: str = None,
            metadata: dict = None,
            selectors: list = None,
            status: str = 'undo',
            fails: int = 0,
            create_time: str = time.strftime('%Y-%m-%d %H:%M:%S')
    ):
        self._bank_name = bank_name
        self._request_type = request_type
        self._url = url
        self._method = method
        self._headers = headers
        self._formdata = formdata or {}
        self._formdata_type = formdata_type
        self._callback = callback
        self._metadata = metadata or {}
        self._selectors = selectors
        self._status = status
        self._fails = fails
        self._create_time = create_time
        self._id = str(farmhash.hash64(self._url + '==' + str(self._formdata)))

    def __repr__(self):
        return f"【bank_name: {self._bank_name}, method: {self._method}, url: {self._url}, headers: {self._headers}, formdata: {self._formdata}, request_type: {self._request_type}, " \
               f"callback: {self._callback}, status: {self._status}, fails: {self._fails}, metadata: {self._metadata}】"

    def do_dump(self):
        elements = [one for one in dir(self) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        data = {}
        for name in elements:
            data[name] = getattr(self, name, None)
        return data

    @classmethod
    def do_load(cls, data: dict):
        target = cls()
        elements = [one for one in dir(cls) if not (one.startswith('__') or one.startswith('_') or one.startswith('do_'))]
        for one in elements:
            if one in data.keys():
                setattr(target, one, data[one])
        return target

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, value):
        self._headers = value

    @property
    def formdata(self):
        return self._formdata

    @formdata.setter
    def formdata(self, value):
        self._formdata = value

    @property
    def formdata_type(self):
        return self._formdata_type

    @formdata_type.setter
    def formdata_type(self, value):
        self._formdata_type = value

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self, value):
        self._callback = value

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        self._metadata = value


    @property
    def bank_name(self):
        return self._bank_name

    @bank_name.setter
    def bank_name(self, value):
        self._bank_name = value

    @property
    def request_type(self):
        return self._request_type

    @request_type.setter
    def request_type(self, value):
        self._request_type = value

    @property
    def selectors(self):
        return self._selectors

    @selectors.setter
    def selectors(self, value):
        self._selectors = value


    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    @property
    def fails(self):
        return self._fails

    @fails.setter
    def fails(self, value):
        self._fails = value

    @property
    def create_time(self):
        return self._create_time

    @create_time.setter
    def create_time(self, value):
        self._create_time = value
