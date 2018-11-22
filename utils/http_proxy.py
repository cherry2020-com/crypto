#!/usr/bin/python
# -*- coding: UTF-8 -*-
import Queue
import random

import os
import requests
import time
from requests import RequestException


class XunDaiLi(object):

    def __init__(self, spider_id, order_no, max_count=5, reuse_count=5,
                 structure='requests'):
        self._spider_id = spider_id
        self._order_no = order_no
        self._max_count = max_count
        self._reuse_count = reuse_count
        self._structure = structure
        self.proxies = Queue.Queue()
        self._session = requests.Session()
        self._base_name = os.path.splitext(os.path.basename(__file__))[0]

    def _test(self):
        pass

    def get_proxy(self):
        if self.proxies.empty():
            while True:
                web_json = self._get()
                error_code, error_msg = self._resolve_error(web_json)
                if error_msg:
                    print error_msg
                if error_code in ['10036', '10038', '10055']:
                    time.sleep(1)
                elif error_code == '10032':
                    raise Exception('Not Enough Proxy')
                else:
                    self._resolve_proxies(web_json)
                    break
        return self.proxies.get(block=False)

    def _get(self):
        url = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp'
        params = {'spiderId': self._spider_id, 'orderno': self._order_no,
                  'count': self._max_count, 'returnType': 2}
        while True:
            try:
                print u'[%s]发送新的请求' % self._base_name
                web_data = self._session.get(url, params=params, timeout=10)
            except RequestException:
                print 'ERROR: request get'
            else:
                if web_data.status_code == 200:
                    break
        return self._session.get(url, params=params).json()

    def _resolve_error(self, web_json):
        error_code_map = {
            '10036': u'[%s]【10036】提取过快，请至少5秒提取一次' % self._base_name,
            '10038': u'[%s]【10038】提取过快，请至少5秒提取一次' % self._base_name,
            '10055': u'[%s]【10055】提取过快，请至少5秒提取一次' % self._base_name,
            '10032': u'[%s]【10032】今日提取已达上限，请隔日提取或额外购买' % self._base_name,
        }
        code = web_json['ERRORCODE']
        return code, error_code_map.get(code)

    def _resolve_proxies(self, web_json):
        proxies = web_json['RESULT']
        all_proxies = []
        for proxy in proxies:
            if self._structure == 'requests':
                p_url = 'http://' + proxy['ip'] + ':' + proxy['port']
                each = {'http': p_url, 'https': p_url}
            else:
                each = proxy
            for _ in range(self._reuse_count):
                all_proxies.append(each)
        random.shuffle(all_proxies)
        for each in all_proxies:
            self.proxies.put(each)


if __name__ == '__main__':
    # p = XunDaiLi('eda47229c37d453b8ea104cb04282113', 'YZ201810105515iB3a1J', max_count=1)
    # print p.get_proxy()
    # print p.get_proxy()
    # print p.get_proxy()
    # print p.get_proxy()
    # print p.get_proxy()
    # print p.get_proxy()
    # 948
    print os.path.splitext(os.path.basename(__file__))
