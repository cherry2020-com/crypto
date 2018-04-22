#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import re

import time

from utils.fiddler import RawToPython
from utils.send_email import Email
email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com', u'斐讯机器人开售！！！')
raw = RawToPython('head_2.txt')
while True:
    try:
        web_data = raw.requests(timeout=10)
        res = re.findall(u'当前最多可售数量:(\\d+?)', web_data.text)
        if res[0] != '0':
            email.send(u'https://mall.phicomm.com/item-17.html')
        elif res[0] == '0':
            print res[0]
    except:
        print 'time out!!!'
    time.sleep(random.randint(5, 20))
