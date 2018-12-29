#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import time

from bs4 import BeautifulSoup

from utils.fiddler_session import RawToPython


DEBUG = True


def get_product_id(entrance_text):
    if DEBUG:
        with open('./head/test.txt') as f:
            entrance_text = f.read()
    bs = BeautifulSoup(entrance_text, "lxml")
    url = bs.find('div', class_='mainbody').find(
        'div', class_='flash-product-list').a.attrs.get('href')
    print u'--> 得到抢购链接: {}'.format(url)
    code = re.findall(r'\d{5,20}', url)[0]
    print u'--> 得到产品ID: {}'.format(code)
    return str(code)


def get_postkey(postkey_text):
    postkey_text = postkey_text.replace(' ', '').replace('"', '')
    postkey = re.findall(r'name=postkeyvalue=\d+', postkey_text)[0]
    yj_id = re.findall(r'name=yj_idvalue=\d', postkey_text)[0]
    print u'--> 得到抢购postkey: {}'.format(postkey)
    print u'--> 得到抢购yj_id: {}'.format(yj_id)
    return postkey, yj_id


if __name__ == '__main__':
    entrance = RawToPython('./head/get_entrance.txt')
    while True:
        entrance_request = entrance.requests()
        print u'--> 入口请求状态码: {}'.format(entrance_request.status_code)
        if entrance_request.status_code == 200:
            product_id = get_product_id(entrance_request.text)
            with open('./head/get_postkey.txt') as f:
                postkey_raw = f.read().format(product_id=product_id)
            postkey = RawToPython(None, postkey_raw)
            postkey.session.cookies = entrance.session.cookies
            postkey_request = postkey.requests()
            print u'--> postkey请求状态码: {}'.format(postkey_request.status_code)
            if postkey_request.status_code == 200:
                post_key, yj_id = get_postkey(postkey_request.text)

                with open('./head/sub_order.txt') as f:
                    sub_order_raw = f.read().format(product_id=product_id,
                                                    postkey=post_key)
                sub_order = RawToPython(None, sub_order_raw)
                sub_order.session.cookies = postkey.session.cookies
                if yj_id:
                    sub_order.set_param(body_param={'yj_id': yj_id})
                sub_order_request = sub_order.requests()
                print u'--> 抢购结果: {}'.format(sub_order_request.text)
                break
        if DEBUG:
            sleep_time = 1
        else:
            sleep_time = 0.01
        time.sleep(sleep_time)
