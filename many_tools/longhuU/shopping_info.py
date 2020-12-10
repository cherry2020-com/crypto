#!/usr/bin/env python
# coding=utf-8

import time

from utils.fiddler import RawToPython
from bs4 import BeautifulSoup

url = 'https://m.uhome.longhu.net/shopping/details/{}'

start_id = 1420877
end_id = 2000000
for _id in xrange(start_id, end_id+1):
    rtp = RawToPython('./shopping_info.txt')
    rtp.set_param(url_param={'id': _id, '_': str(int(time.time()*1000))})
    try:
        rtp_web = rtp.requests(timeout=10)
    except:
        try:
            rtp_web = rtp.requests(timeout=10)
        except:
            try:
                rtp_web = rtp.requests(timeout=10)
            except:
                continue
    rtp_json = rtp_web.json()
    if rtp_json['code'] == 500:
        continue
    rtp_json = rtp_json['data']['entity']
    rtp_json['price'] = float(rtp_json['price'])
    rtp_json['originalPrice'] = float(rtp_json['originalPrice'])
    chajia = rtp_json['originalPrice'] - rtp_json['price']
    if ((rtp_json['price'] <= 100 and chajia >= 50)
            or (chajia >= 100)
            or rtp_json['price'] <= 10):
        print u'\033[1;35m id: {}, name: {}, price: {}, org_price: {}, chajia: {} \033[0m'.format(
            _id, rtp_json['goodsName'], rtp_json['price'], rtp_json['originalPrice'], chajia)
    elif u'小米' in rtp_json['goodsDesc'] or u'小米' in rtp_json['goodsName']:
        print u'\033[1;35m KEYWORD: 小米, id: {}, name: {}, price: {}, org_price: {}, chajia: {} \033[0m'.format(
            _id, rtp_json['goodsName'], rtp_json['price'], rtp_json['originalPrice'], chajia)
    else:
        print u'id: {}, name: {}, price: {}, org_price: {}, chajia: {}'.format(
            _id, rtp_json['goodsName'], rtp_json['price'], rtp_json['originalPrice'], chajia)
    # time.sleep(1)

