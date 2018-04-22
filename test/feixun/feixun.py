#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import re

import time

from utils.fiddler import RawToPython
from utils.send_email import Email
email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com', u'斐讯机器人开售！！！')
raw = RawToPython('head.txt')
flag = 0
while True:
    try:
        web_data = raw.requests(timeout=10)
        res = re.findall(u'已售(.+?)件', web_data.text)
        if res[0] != '8241':
            email.send(u'https://mall.phicomm.com/item-17.html')
            flag += 1
        print res[0]
    except:
        print 'time out!!!'
    if flag == 5:
        break
    time.sleep(random.randint(5, 20))
