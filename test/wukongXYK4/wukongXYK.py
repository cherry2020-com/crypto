#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

import requests
import time

from utils.fiddler import RawToPython
from utils.jiema import YiMa
from utils.user_agents import UserAgents

mobile = None
jiema = YiMa(28015)
ua = UserAgents()
p_url = None
while True:
    try:
        if not p_url:
            get_p = requests.get('http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=eda47229c37d453b8ea104cb04282113&orderno=YZ201810105515iB3a1J&returnType=2&count=1')
            p_json = get_p.json()['RESULT'][0]
            p_url = ('http://' + p_json['ip'] + ':' + p_json['port'])
        print p_url
        mobile = jiema.get_mobile()
        nua = ua.get_random()
        print '-->', nua
        fd = RawToPython('1head')
        fd.headers['User-Agent'] = nua
        fd.set_param(req_param={'mobile': mobile})
        web_data = fd.requests(proxies={'http': p_url, 'https': p_url})
        print web_data.text
        if web_data.json()['code'] != 0:
            print '-->', 'mobile error'
            raise Exception('mobile error')
        code = jiema.get_sms_code(mobile=mobile)
        fd2 = RawToPython('2head')
        fd2.set_param(req_param={'username': mobile, 'code': code})
        fd2.headers['User-Agent'] = nua
        fd2_json = fd2.requests(proxies={'http': p_url, 'https': p_url}).json()
        print fd2_json
        fd3 = RawToPython('head3')
        fd3.headers['Authorization'] = fd2_json['data']
        fd3.headers['User-Agent'] = nua
        fd3_json = fd3.requests(proxies={'http': p_url, 'https': p_url}).json()
        print fd3_json['data']['cutAmount']
        if fd3_json['data']['cutAmount'] < 2:
            break
    except:
        jiema.release_mobile(mobile)
    else:
        sleep = random.randint(10, 30)
        print '---> sleep %ss' % sleep
        time.sleep(sleep)
        p_url = None
