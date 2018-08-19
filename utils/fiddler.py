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
        self.method = None
        self.url = None
        self.headers = None
        self.req_data = None
        self.req_json = None
        self.req_param = None
        self.url_parse = None
        self.__file = file_name
        self.__raw = file_raw
        self.__lines = None
        self.__is_https = is_https
        self.__get_raw()
        self.__to_python()

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
                if self.headers.get("Referer"):
                    http_host = self.headers.get("Referer").split(":", 1)[0]
                elif self.headers.get("Origin"):
                    http_host = self.headers.get("Origin").split(':', 1)[0]
                else:
                    http_host = "https"
            else:
                http_host = "https" if self.__is_https else "http"
            http_host += "://" + self.headers["Host"]
            self.url = http_host + self.url
        self.url_parse = urlparse.urlparse(self.url)

    def __to_headers(self):
        ready_to_dict = []
        for line in self.__lines[1:]:
            line = line.strip()
            if not line:
                break
            line_split = line.split(":", 1)
            line_split = [each.strip() for each in line_split]
            ready_to_dict.append(line_split)
        self.headers = OrderedDict(ready_to_dict)

    def __to_body(self):
        if self.__lines[-2].strip():
            return
        body_data = urllib.unquote(self.__lines[-1])
        line = body_data.strip("&")
        try:
            self.req_json = json.loads(line)
        except Exception:
            line_split = line.split("&")
            ready_to_dict = []
            for each in line_split:
                ready_to_dict.append(each.split("=", 1))
            self.req_data = OrderedDict(ready_to_dict)

    def __to_python(self):
        self.__to_headers()
        self.__to_method_and_url()
        self.__to_body()

    def __set_url_param(self, param):
        if not isinstance(param, dict):
            raise FiddlerError("param must be dict")
        base_url = self.url_parse.scheme + "://" + self.url_parse.netloc + \
                   self.url_parse.path
        url_param = dict([(k, v[0]) for k, v in urlparse.parse_qs(
            self.url_parse.query).items()])
        url_param.update(param)
        logging.debug("fd: set_url_param: " + str(param))
        self.url = base_url + '?' + urllib.urlencode(url_param)
        self.url_parse = urlparse.urlparse(self.url)

    def set_param(self, url_param=None, req_param=None):
        if url_param:
            self.__set_url_param(url_param)
        self.req_param = {"url": self.url,
                          "headers": self.headers}
        if self.method == "POST":
            if self.req_data:
                if req_param:
                    self.req_data.update(req_param)
                self.req_param["data"] = self.req_data
                logging.debug("fd: set_date_param: " + str(req_param))
            elif self.req_json:
                if req_param:
                    self.req_json.update(req_param)
                # self.req_param["json"] = self.req_json
                self.req_param["data"] = json.dumps(self.req_json)
                logging.debug("fd: set_json_param: " + str(req_param))

    def __reset_req_param(self, req_param):
        if self.url != req_param['url']:
            req_param['headers']['HOST'] = urlparse.urlsplit(req_param['url']).netloc

    def requests(self, is_test=False, auto_parm=True, **kwargs):
        """
        url=None, data=None, json=None, headers=None, timeout=None
        """
        if auto_parm:
            self.set_param()
        req_param = self.req_param
        req_param.update(kwargs)
        self.__reset_req_param(req_param)
        if is_test:
            url_list = req_param["url"].split("/", 3)
            url_list[2] = "127.0.0.1"
            req_param["url"] = "/".join(url_list)
        if self.method == "GET":
            try:
                web_data = requests.get(verify=False, **req_param)
                return web_data
            except requests.Timeout as e:
                error_msg = "{time}: fd: requests get error: {url}: {e}".format(
                    time=datetime.datetime.now(), url=req_param["url"], e=e)
                logging.error(error_msg)
                raise FiddlerRequestTimeOutException(error_msg)
            except Exception as e:
                error_msg = "{time}: fd: requests get error: {url}: {e}".format(
                    time=datetime.datetime.now(), url=req_param["url"], e=e)
                logging.error(error_msg)
                raise FiddlerRequestException(error_msg)
        elif self.method == "POST":
            try:
                web_data = requests.post(verify=False, **req_param)
                return web_data
            except requests.Timeout as e:
                error_msg = "{time}: fd: requests post error: {url}: {e}".format(
                    time=datetime.datetime.now(), url=req_param["url"], e=e)
                logging.error(error_msg)
                raise FiddlerRequestTimeOutException(error_msg)
            except Exception as e:
                error_msg = "{time}: fd: requests post error: {url}: {e}".format(
                    time=datetime.datetime.now(), url=req_param["url"], e=e)
                logging.error(error_msg)
                raise FiddlerRequestException(error_msg)
