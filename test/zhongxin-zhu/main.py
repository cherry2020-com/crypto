#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

import time

from utils.fiddler import RawToPython


goodsIds = {
    u'琉璃猪': 'mcs2018182610007',
    u'珍宝猪': 'mcs2018182610002',
    u'七龙猪': 'mcs2018182610012',
    u'元宝猪': 'mcs2018182610018',
    u'夜明猪': 'mcs2018182610014',
    u'黑珍猪': 'mcs2018182610006',
}
Cookie = 'citicbank=4360a3b49d0a8b0ee02de8312f9a2552; Path=/; JSESSIONID_BASEH5=178FD9425168F0CCA95F1B714A192D96; Domain=.creditcard.ecitic.com; JSESSIONID_OAUTH=178FD9425168F0CCA95F1B714A192D96; citicbank_cookie=!qp7bafbfXfN5Mci7WDSPiZPLSyIDtCKAOGujvplv+SbeTYBD4vhrHOgCW5Exvu4x2LZ/TC7KOMXLIkE; path=/;'
use_tool_fd = RawToPython('./head/used_tool.txt')
use_tool_fd.set_head(Cookie=Cookie)
start_fd = RawToPython('./head/start.txt')
start_fd.set_head(Cookie=Cookie)
tu_fd = RawToPython('./head/tu.txt')
tu_fd.set_head(Cookie=Cookie)

while True:
    try:
        while True:
            start_json = start_fd.requests().json()
            if start_json["retCode"] == "000000":
                break
            print start_json['retMsg']
        s_pigTypeId = start_json['data']['pig']['pigTypeId']
        s_pigTypeName = start_json['data']['pig']['pigTypeName']
        s_totalApply = start_json['data']['pig']['totalApply']
        s_residue = start_json['data']['residue']
        if s_residue <= 0:
            break
        print(u'拥有刷子:{};;当前猪：{}-{};;需要刷子：{};;'.format(
            s_residue, s_pigTypeId, s_pigTypeName, s_totalApply))
        if s_pigTypeName in goodsIds:
            use_tool_fd.set_param(req_param={'goodsId': goodsIds[s_pigTypeName]})
            use_json = use_tool_fd.requests().json()
            print u'使用道具-->{}'.format(use_json['retMsg'])
        if s_pigTypeName == u'夜明猪':
            secs = ['face', 'body', 'earright', 'earleft', 'handright', 'handleft', 'nose', 'pants', 'footleft', 'footright']
        elif s_pigTypeName == u'七龙猪':
            secs = ['face', 'body', 'earright', 'earleft', 'handright', 'handleft', 'nose', 'hair', 'footleft', 'footright']
        else:
            secs = ['face', 'body', 'nose', 'hand', 'foot']
        colors = ['blue', 'gold', 'green', 'black', 'red']
        random.shuffle(secs)
        for sec in secs:
            color = random.choice(colors)
            tu_fd.set_param(req_param={"userApply": {"sec": sec, "color": color}})
            r = tu_fd.requests()
            if 'goodsName' in r.text:
                print(u"{}-->{}-->{}".format(
                    sec, r.json()['data']['lotteryData']['goodsName'],
                    r.json()['data']['lotteryData']['goodsDesc']))
            else:
                print(u"{}-->{}".format(sec, r.json()['retMsg']))
            sleep_time = random.randint(3, 5)
            print '-->', sleep_time, 's'
            time.sleep(sleep_time)
    except Exception:
        pass