#!/usr/bin/env python
import re
import json
from typing import Union, Pattern
from lxml import etree
from bs4 import BeautifulSoup, UnicodeDammit
from bs4.element import Tag, NavigableString
from urllib.parse import urlparse, urljoin
from .exceptions import NothingMatchedError
from copy import copy


class BaseField(object):

    def __init__(self, default="", many: bool = False, callback: str = None, url_prefix: str = None):
        self.default = default
        self.many = many
        self.callback = callback
        self.url_prefix = url_prefix

    def extract(self, *args, **kwargs):
        raise NotImplementedError("extract is not implemented.")


class _Bs4Field(BaseField):

    def __init__(
            self,
            name: Union[str, list, Pattern, bool] = None,
            attrs: dict = None,
            metadata: dict = None,
            cssdata: dict = None,
            recursive: bool = True,                             # bs4默认遍历查找tag的所有子孙节点，如果只想搜索tag的直接子节点,可以设置recursive=False
            string: Union[str, list, Pattern, bool] = None,
            css_select: str = None,
            default=None,
            many: bool = True,
            callback: str = None,
            url_prefix: str = None
    ):
        super().__init__(default=default, many=many, callback=callback, url_prefix=url_prefix)
        self.name = name
        self.attrs = attrs or {}
        self.metadata = metadata or {}
        self.cssdata = cssdata or {}
        self.recursive = recursive
        self.string = string
        self.css_select = css_select
        self.limit = 1 if many is False else None

    def extract(self, soup: Union[str, BeautifulSoup, Tag], is_source: bool = False):
        if isinstance(soup, str):
            soup = BeautifulSoup(soup, 'lxml')

        elements = self._get_elements(soup=soup)
        # 如果是target_item，则表明是一个预先提取的部分，为source, 供后续使用soup继续提取
        # 此处需要判断elements集合中的成员，是Tag类型还是NavigableString类型，因为只有Tag类型，才支持soup继续查找；
        # NavigableString 对象支持 遍历文档树 和 搜索文档树 中定义的大部分属性, 但并非全部。
        # 尤其是,一个字符串不能包含其它内容(tag能够包含字符串或是其它tag), 字符串不支持.contents 或 .string 属性或 find() 方法。
        if is_source:
            if elements and type(elements[0]) == Tag:
                return elements
            else:
                raise NothingMatchedError(f"BeautifulSoup is_source but No Tag found")

        if elements:
            if type(elements[0]) == Tag:
                results = [self._parse_element(one) for one in elements]
            elif type(elements[0]) == NavigableString:
                results = [self._unicode_value(one) for one in elements]
            else:
                raise NothingMatchedError(f"BeautifulSoup parsed result type is neither Tag nor NavigableString")
        elif self.default:
            results = self.default if type(self.default) == list else [self.default]
        else:
            raise NothingMatchedError(f"BeautifulSoup find Nothing, name:%s, attrs:%s, string:%s, css_select:%s, url_prefix:%s" % (self.name, self.attrs, self.string, self.css_select, self.url_prefix))
        return results if not self.limit else results[0]

    def _unicode_value(self, string: NavigableString):
        value = UnicodeDammit.detwingle(string)
        return UnicodeDammit(value).unicode_markup

    def _get_elements(self, *, soup: Union[BeautifulSoup, Tag]):
        if self.css_select:
            elements = soup.select(selector=self.css_select, limit=self.limit)
        else:
            elements = soup.find_all(name=self.name, attrs=self.attrs, recursive=self.recursive, text=self.string, limit=self.limit)
        return elements

    def _parse_element(self, element):
        raise NotImplementedError


class Bs4HtmlField(_Bs4Field):
    def _parse_element(self, element):
        if type(element) == BeautifulSoup or type(element) == Tag:
            return element
        else:
            return BeautifulSoup(element, 'lxml')


class Bs4TextField(_Bs4Field):

    def __init__(
            self,
            separator: str = None,
            name: Union[str, list, Pattern, bool] = None,
            attrs: dict = None,
            metadata: dict = None,
            cssdata: dict = None,
            recursive: bool = True,
            string: Union[str, list, Pattern, bool] = None,
            css_select: str = None,
            default=None,
            many: bool = True,
            callback: str = None,
            url_prefix: str = None
    ):
        super().__init__(
            name=name,
            attrs=attrs,
            metadata=metadata,
            cssdata=cssdata,
            recursive=recursive,
            string=string,
            css_select=css_select,
            default=default,
            many=many,
            callback=callback,
            url_prefix=url_prefix
        )
        self.separator = separator

    def _parse_element(self, element):
        if self.separator:
            string = element.get_text(self.separator, strip=True)
        else:
            string = element.get_text(strip=True)
        return string if string else self.default


class Bs4AttrField(_Bs4Field):

    def __init__(
            self,
            target: str,
            name: Union[str, list, Pattern, bool] = None,
            attrs: dict = None,
            metadata: dict = None,
            cssdata: dict = None,
            recursive: bool = True,
            string: Union[str, list, Pattern, bool] = None,
            css_select: str = None,
            default=None,
            many: bool = True,
            callback: str = None,
            url_prefix: str = None
    ):
        super().__init__(
            name=name,
            attrs=attrs,
            metadata=metadata,
            cssdata=cssdata,
            recursive=recursive,
            string=string,
            default=default,
            css_select=css_select,
            many=many,
            callback=callback,
            url_prefix=url_prefix
        )
        self.target = target

    def _parse_element(self, element):
        attr = element.get(self.target, self.default)
        attr = attr.strip()
        if self.url_prefix and self.target == 'href':
            if '%s' in self.url_prefix:
                attr = self.url_prefix % attr
            else:
                if not attr.startswith('http'):
                    attr = urljoin(self.url_prefix, attr)

        # metadata一定要拷贝，否则出错，此处用于农行下载图片
        metadata = copy(self.metadata)
        if metadata:
            metadata['attr'] = attr
            return metadata
        return attr



class Bs4AttrTextField(_Bs4Field):

    def __init__(
            self,
            target: str,
            separator: str = None,
            name: Union[str, list, Pattern, bool] = None,
            attrs: dict = None,
            metadata: dict = None,
            cssdata: dict = None,
            recursive: bool = True,
            string: Union[str, list, Pattern, bool] = None,
            css_select: str = None,
            default=None,
            many: bool = True,
            callback: str = None,
            url_prefix: str = None
    ):
        super().__init__(
            name=name,
            attrs=attrs,
            metadata=metadata,
            cssdata=cssdata,
            recursive=recursive,
            string=string,
            default=default,
            css_select=css_select,
            many=many,
            callback=callback,
            url_prefix=url_prefix
        )
        self.target = target
        self.separator = separator

    def _parse_element(self, element):
        attr = element.get(self.target, self.default)
        attr = attr.strip()
        if self.separator:
            string = element.get_text(self.separator, strip=True)
        else:
            string = element.get_text(strip=True)
        text = string if string else self.default

        if self.url_prefix and self.target == 'href':
            if '%s' in self.url_prefix:
                attr = self.url_prefix % attr
            else:
                if not attr.startswith('http'):
                    attr = urljoin(self.url_prefix, attr)

        # 一定要复制metadata,否则会出错
        metadata = copy(self.metadata)
        if metadata:
            metadata['text'] = text
            metadata['attr'] = attr
            return metadata
        return {'text': text, 'attr': attr}


class _LxmlElementField(BaseField):

    def __init__(self, css_select: str = None, xpath_select: str = None, default=None, many: bool = False, callback: str = None, url_prefix: str = None):
        super().__init__(default=default, many=many, callback=callback, url_prefix=url_prefix)
        self.css_select = css_select
        self.xpath_select = xpath_select

    def extract(self, html_etree: etree._Element, is_source: bool = False):
        elements = self._get_elements(html_etree=html_etree)
        # 如果是target_item，则表明是一个预先提取的部分，为source
        if is_source:
            return elements if self.many else elements[0]

        # 如果不是target_item，但通过css_select或xpath_select提取出来的elements有值
        if elements:
            # 则根据子类AttrField，HtmlField，TextField重写的_parse_element()方法，提取出elements集合
            results = [self._parse_element(element) for element in elements]
        elif self.default is None:
            # 如果self.default则返回错误提示：_LxmlElementField需要有selector或者default值
            raise NothingMatchedError(
                f"Extract `{self.css_select or self.xpath_select}` error, "
                f"please check selector or set parameter named `default`"
            )
        else:
            # 如果如果不是target_item，也没有通过css_select或xpath_select提取出来的elements，也没有传递进来的default值
            # 则返回default=None
            results = self.default if type(self.default) == list else [self.default]
        # 如果self.many为True, 则返回results集合，否则返回results集合中的第一个元素
        return results if self.many else results[0]

    def _get_elements(self, *, html_etree: etree._Element):
        if self.css_select:                                           # 如果self.css_select为True, 则使用cssselect()方法来提取elements, etree会匹配所有符合条件的dom
            elements = html_etree.cssselect(self.css_select)
        elif self.xpath_select:                                       # 如果self.xpath_select为True, 则使用xpath()方法来提取elements, etree会匹配所有符合条件的dom
            elements = html_etree.xpath(self.xpath_select)
        else:
            raise ValueError(f"{self.__class__.__name__} field: css_select or xpath_select is expected")
        if not self.many:                                             # 如果self.many不为True, 则返回elements的第一个记录， 否则全部返回
            elements = elements[:1]
        return elements

    def _parse_element(self, element):
        raise NotImplementedError


class AttrField(_LxmlElementField):
    def __init__(self, attr, css_select: str = None, xpath_select: str = None, default="", many: bool = False, callback: str = None, url_prefix: str = None):
        super().__init__(css_select=css_select, xpath_select=xpath_select, default=default, many=many, callback=callback, url_prefix=url_prefix)
        self.attr = attr

    def _parse_element(self, element):
        return element.get(self.attr, self.default)


class HtmlField(_LxmlElementField):
    def _parse_element(self, element):
        return etree.tostring(element, encoding="utf-8").decode(encoding="utf-8")


class TextField(_LxmlElementField):
    def _parse_element(self, element):
        if isinstance(element, etree._ElementUnicodeResult):
            strings = [node for node in element]
        else:
            strings = [node.strip() for node in element.itertext()]
        string = "".join(strings)
        return string if string else self.default


class RegexField(BaseField):
    def __init__(self, re_select: str, re_flags=0, default="", many: bool = False, callback: str = None, url_prefix: str = None):
        super().__init__(default=default, many=many, callback=callback, url_prefix=url_prefix)
        self._re_select = re_select
        self._re_object = re.compile(self._re_select, flags=re_flags)

    def _parse_match(self, match):
        if not match:
            if self.default:
                return self.default
            else:
                raise NothingMatchedError(
                    f"Extract `{self._re_select}` error, "
                    f"please check selector or set parameter named `default`"
                )
        else:
            string = match.group()
            groups = match.groups()
            group_dict = match.groupdict()
            if group_dict:
                return group_dict
            if groups:
                return groups[0] if len(groups) == 1 else groups
            return string

    def extract(self, html: Union[str, etree._Element, BeautifulSoup, Tag]):
        if isinstance(html, etree._Element):                                # 如果html是etree._Element实例，则将其转为string格式
            html = etree.tostring(html).decode(encoding="utf-8")
        elif isinstance(html, BeautifulSoup) or isinstance(html, Tag):
            html = html.prettify()

        if self.many:                                                       # 如果many是True, 则多处匹配正则寻找
            matches = self._re_object.finditer(html)
            return [self._parse_match(match) for match in matches]
        else:                                                               # 如果不是many, 则仅使用正则的search()方法寻找单处
            match = self._re_object.search(html)
            return self._parse_match(match)


# JsonField只适用于async for进行迭代，不能使用await item否则会报错
class JsonField(BaseField):
    def __init__(self, json_select: str = None, default=None, many: bool = False, callback: str = None, url_prefix: str = None):
        super().__init__(default=default, many=many, callback=callback, url_prefix=url_prefix)
        self.json_select = json_select

    # 根据json_select的层级数，一层一层的提取json数据，例如json_select="a>b>c"
    def _get_elements(self, jsondata: json):
        if not self.json_select:
            return self.default

        list_select = self.json_select.split('>')
        for one in list_select:
            jsondata = jsondata[one]
        return jsondata

    # 根据json_select，从json数据中，提取出值，例如title = JsonField(json_select="e")
    def extract(self, jsondata: json):
        return self._get_elements(jsondata=jsondata)


class JsonMultiField(BaseField):
    def __init__(self, json_select: str = None, default=None, many: bool = False, callback: str = None, url_prefix: str = None):
        super().__init__(default=default, many=many, callback=callback, url_prefix=url_prefix)
        self.json_select = json_select

    # 根据json_select的层级数，一层一层的提取json数据，例如json_select="a>b>c"
    def _get_elements(self, jsondata: json):
        if not self.json_select:
            return self.default

        jsondata_need = {}
        list_select = self.json_select.split('=')
        for one in list_select:
            jsondata_need[one] = jsondata[one]

        if self.url_prefix and ('url' in jsondata_need.keys()):
            url = jsondata_need['url']
            if not url.startswith('http'):
                jsondata_need['url'] = self.url_prefix + url

        return jsondata_need

    # 根据json_select，从json数据中，提取出值，例如title = JsonField(json_select="e")
    def extract(self, jsondata: json):
        return self._get_elements(jsondata=jsondata)


# 格式：json_select='annoId=url,annoTitle=title,annoDate=date'
class JsonDictMultiField(JsonField):

    def _get_elements(self, jsondata: json):
        if not self.json_select:
            return self.default

        jsondata_need = {}
        list_select = self.json_select.split(',')
        for one in list_select:
            list_one = one.split('=')
            key = list_one[0]
            value = list_one[1]
            jsondata_need[value] = jsondata[key]

        if 'url' in jsondata_need.keys():
            url = jsondata_need['url']
            if type(url) != str:
                url = str(url)
                jsondata_need['url'] = url

            if self.url_prefix:
                if '%s' in self.url_prefix:
                    jsondata_need['url'] = self.url_prefix % url
                else:
                    if not url.startswith('http'):
                        jsondata_need['url'] = self.url_prefix + url

        return jsondata_need
