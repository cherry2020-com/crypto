#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

from utils.fiddler import RawToPython
from utils.http_proxy import XunDaiLi

wb = RawToPython('./head.txt')
# key=62662236



random_id = 63667401
# random_id = 35694701
p = XunDaiLi('eda47229c37d453b8ea104cb04282113', 'YZ201810105515iB3a1J',
             max_count=1, reuse_count=2)
proxy = p.get_proxy()
print proxy
right_codes = []
exist_right_codes = ''
while True:
    try:
        wb.set_param(url_param={'key': str(random_id)})
        req = wb.requests(proxies=proxy, timeout=10)
        print req.text.strip()
        json = req.json()
        print json['msg'], random_id
        if json['msg'] == u"验证通过":
            print '--------->', random_id
            with open('./codes.txt') as f:
                exist_right_codes = f.read()
            with open('./codes.txt', 'wb+') as f:
                f.write(exist_right_codes + ', ' + str(random_id))
        random_id += 1
        time.sleep(0.1)
    except:
        proxy = p.get_proxy()
        time.sleep(1)
        print '--> request error'
