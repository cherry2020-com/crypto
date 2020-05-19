#!/usr/bin/env python
# coding=utf-8
"""
verify=False Requests 也能忽略对 SSL 证书的验证
cert=('/path/server.crt', '/path/key') 也可以指定一个本地证书用作客户端证书

author = "minglei.weng@dianjoy.com"
created = "2016/10/14 0014"
"""
import json
import urllib
import urlparse
from collections import OrderedDict
import logging
import datetime

import requests
import urllib3
from func_timeout import func_set_timeout
from requests.cookies import cookiejar_from_dict
from requests.structures import CaseInsensitiveDict

from utils import settings


urllib3.disable_warnings()


class FiddlerRequestException(Exception):
    pass


class FiddlerRequestTimeOutException(FiddlerRequestException):
    pass


class FiddlerError(Exception):
    def __init__(self, info):
        self.info = info

    def __str__(self):
        return repr(self.info)


class RawToPython(object):
    def __init__(self, file_name=None, file_raw=None, is_https=None):
        if not (file_name or file_raw):
            raise FiddlerError("must had file_name or file_data")
        self.session = requests.Session()
        self.method = None
        self.__url_host = None
        self.url = None
        self.body_data = None
        self.body_json = None
        self.req_param = None
        self.url_parse = None
        self.__file = file_name
        self.__raw = file_raw
        self.__lines = None
        self.__is_https = is_https
        self.__get_raw()
        self.__to_python()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def __get_raw(self):
        if self.__file:
            with open(self.__file, "rb") as f:
                self.__raw = f.read().strip()
        self.__lines = self.__raw.splitlines()

    def __to_method_and_url(self):
        line_split = self.__lines[0].strip().split(" ")
        line_split = filter(lambda ch: ch,
                            [each.strip() for each in line_split])
        self.method = line_split[0]
        self.url = line_split[1]
        if not self.url.startswith("http"):
            if self.__is_https is None:
                if self.session.headers.get("Referer"):
                    http_host = self.session.headers.get("Referer").split(":", 1)[0]
                elif self.session.headers.get("Origin"):
                    http_host = self.session.headers.get("Origin").split(':', 1)[0]
                else:
                    http_host = "https"
            else:
                http_host = "https" if self.__is_https else "http"
            http_host += "://" + self.session.headers["Host"]
            self.__url_host = http_host
            self.url = http_host + self.url
        self.url_parse = urlparse.urlparse(self.url)
        self.__url_host = self.url_parse.scheme + '://' + self.url_parse.netloc

    def __to_headers(self):
        self.session.headers = CaseInsensitiveDict()
        for line in self.__lines[1:]:
            line = line.strip()
            if not line:
                break
            head_key, head_value = line.split(":", 1)
            head_key = head_key.strip()
            head_value = head_value.strip()
            if head_key.lower() == 'cookie':
                self.__to_cookie(head_value)
                continue
            self.session.headers[head_key] = head_value

    def __to_body(self):
        if self.__lines[-2].strip():
            return
        body_data = urllib.unquote(self.__lines[-1])
        line = body_data.strip("&")
        try:
            self.body_json = json.loads(line)
        except ValueError:
            line_split = line.split("&")
            ready_to_dict = []
            for each in line_split:
                ready_to_dict.append(each.split("=", 1))
            self.body_data = OrderedDict(ready_to_dict)

    def __to_cookie(self, raw_cookie):
        cookies = raw_cookie.strip(';').split('; ')
        cookies_dict = OrderedDict()
        for cookie in cookies:
            cookie_key, cookie_value = cookie.split('=', 1)
            cookies_dict[cookie_key] = cookie_value
        self.session.cookies = cookiejar_from_dict(cookies_dict)

    def __to_python(self):
        self.__to_headers()
        self.__to_method_and_url()
        self.__to_body()

    def __set_url_param(self, param):
        if not isinstance(param, dict):
            raise FiddlerError("param must be dict")
        base_url = (self.url_parse.scheme + "://" + self.url_parse.netloc +
                    self.url_parse.path)
        url_param = dict([(k, v[0]) for k, v in urlparse.parse_qs(
            self.url_parse.query).items()])
        url_param.update(param)
        logging.debug("fd: set_url_param: " + str(param))
        self.url = base_url + '?' + urllib.urlencode(url_param)
        self.url_parse = urlparse.urlparse(self.url)

    def set_param(self, url_param=None, body_param=None):
        if url_param is not None:
            self.__set_url_param(url_param)
        self.req_param = {"url": self.url}
        if self.body_data is not None:
            if body_param is not None:
                self.body_data.update(body_param)
            self.req_param["data"] = self.body_data
            logging.debug("fd: set_body_param: " + str(body_param))
        elif self.body_json is not None:
            if body_param is not None:
                self.body_json.update(body_param)
            # self.req_param["json"] = self.body_json
            self.req_param["data"] = json.dumps(self.body_json)
            logging.debug("fd: set_json_param: " + str(body_param))

    def set_head(self, **kwargs):
        self.session.headers.update(kwargs)

    def __reset_req_param(self, req_param):
        if req_param['url'].startswith(self.__url_host + '/'):
            return
        self.session.headers['HOST'] = urlparse.urlsplit(req_param['url']).netloc

    def __requests_reset_url(self, req_param, reset_url):
        if not reset_url:
            return
        if reset_url.startswith('http'):
            req_param["url"] = reset_url
        else:
            if reset_url.startswith('/'):
                req_param["url"] = self.__url_host + reset_url
            else:
                req_param["url"] = self.__url_host + '/' + reset_url

    @func_set_timeout(10)
    def requests(self, reset_url=None, is_test=False, auto_parm=True, **kwargs):
        """
        url=None, data=None, json=None, headers=None, timeout=None
        """
        if auto_parm:
            self.set_param()
        req_param = self.req_param
        req_param.update(kwargs)
        if 'timeout' not in req_param:
            req_param['timeout'] = 10
        self.__requests_reset_url(req_param, reset_url)
        self.__reset_req_param(req_param)
        if is_test:
            url_list = req_param["url"].split("/", 3)
            url_list[2] = "127.0.0.1"
            req_param["url"] = "/".join(url_list)
        try:
            web_data = getattr(self.session, self.method.lower())(
                verify=False, **req_param)
            return web_data
        except requests.Timeout as e:
            error_msg = "{time}: fd: requests get error: {url}: {e}".format(
                time=datetime.datetime.now(), url=req_param["url"], e=e)
            logging.exception(error_msg)
            raise FiddlerRequestTimeOutException(error_msg)
        except Exception as e:
            error_msg = "{time}: fd: requests get error: {url}: {e}".format(
                time=datetime.datetime.now(), url=req_param["url"], e=e)
            logging.exception(error_msg)
            raise FiddlerRequestException(error_msg)
