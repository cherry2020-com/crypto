#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import random

import time

from utils.fiddler_session import RawToPython

CUR_DIR = os.path.dirname(os.path.abspath(__file__))
web_data = RawToPython(os.path.join(CUR_DIR, 'head.txt'))
count = 0
ids = ['175', '7']
while True:
    count += 1
    shop_id = ids[count % 2]
    web_data.set_param(url_param={'id': shop_id})
    try:
        j = web_data.requests().json()
    except:
        continue
    try:
        if j['is_busy'] == 1:
            print u'[x][%s][%s]is busy' % (count, j['name'])
        else:
            tip_temp = u"""osascript -e 'display notification "{content}" with title "{title}"'""".format(
                content=u'快快快，可以买【{}】的喜茶啦！'.format(j['name']), title=u'喜茶')
            import os
            os.system(tip_temp.encode('utf-8'))
            print u'[v] go go go shopping!!!!'
            break
    except:
        print '-->', j
        print '-->', shop_id
    time.sleep(random.randint(3, 10))
