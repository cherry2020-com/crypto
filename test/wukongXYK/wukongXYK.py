#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

import requests
import time

from utils.fiddler import RawToPython
from utils.http_proxy import XunDaiLi
from utils.jiema import YiMa
from utils.user_agents import UserAgents

mobile = None
jiema = YiMa(28015)
ua = UserAgents()
p = XunDaiLi('eda47229c37d453b8ea104cb04282113', 'YZ201810105515iB3a1J', max_count=1)
while True:
    try:
        each_p = p.get_proxy()
        print each_p['http']
        mobile = jiema.get_mobile()
        nua = ua.get_random()
        print '-->', nua
        fd = RawToPython('1head')
        fd.headers['User-Agent'] = nua
        fd.set_param(req_param={'mobile': mobile})
        web_data = fd.requests(proxies=each_p)
        print web_data.text
        if web_data.json()['code'] != 0:
            print '-->', 'mobile error'
            raise Exception('mobile error')
        code = jiema.get_sms_code(mobile=mobile)
        fd2 = RawToPython('2head')
        fd2.set_param(req_param={'username': mobile, 'code': code})
        fd2.headers['User-Agent'] = nua
        fd2_json = fd2.requests(proxies=each_p).json()
        print fd2_json
        fd3 = RawToPython('head3')
        fd3.headers['Authorization'] = fd2_json['data']
        fd3.headers['User-Agent'] = nua
        fd3_json = fd3.requests(proxies=each_p).json()
        print fd3_json['data']['cutAmount']
        if fd3_json['data']['cutAmount'] < 2:
            break
    except:
        jiema.release_mobile(mobile)
    else:
        sleep = random.randint(10, 30)
        print '---> sleep %ss' % sleep
        time.sleep(sleep)
