#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re

import requests
import time


class YiMa(object):
    """
    http://www.51ym.me
    """
    def __init__(self, item_id, token='0101454744924a6c4188dfeed50390c0a54c609c1d01'):
        self.url = 'http://api.fxhyd.cn/UserInterface.aspx'
        self.token = token
        self.item_id = item_id
        self._is_release_mobile = True

    def login(self, username, password):
        pass

    def get_mobile(self, isp=None, province=None, city=None,
                   mobile=None, excludeno=None):
        params = {'action': 'getmobile', 'token': self.token,
                  'itemid': self.item_id}
        if excludeno:
            params['excludeno'] = excludeno
        # TODO other
        web_data = requests.get(self.url, params)
        if web_data.status_code == 200:
            print '--> get_number:', web_data.text
            mobile = web_data.text.replace('success|', '')
            if not mobile.isalnum():
                raise Exception('get number error: ' + mobile)
            self._is_release_mobile = False
            return mobile
        raise Exception('get number error: ' + web_data.text)

    def release_mobile(self, mobile):
        if self._is_release_mobile:
            print '--> had release mobile'
            return
        params = {'action': 'release', 'token': self.token,
                  'itemid': self.item_id, 'mobile': mobile}
        web_data = requests.get(self.url, params)
        if web_data.status_code == 200:
            if web_data.text.startswith('success'):
                print '--> release mobile success'
            else:
                print '--> explanation:', self.get_error(web_data.text)
            self._is_release_mobile = True
        else:
            raise Exception('release mobile error: ' + web_data.status_code)

    def get_sms_code(self, sms=None, regx=r'\d{6}', **kwargs):
        if not sms:
            sms = self.get_sms(**kwargs)
        codes = re.findall(regx, sms)
        if len(codes) == 1:
            return codes[0]
        raise Exception(u'find sms code error: %s' % codes)

    def get_sms(self, mobile=None, release=1, getsendno=None):
        params = {'action': 'getsms', 'token': self.token,
                  'itemid': self.item_id}
        if mobile:
            params['mobile'] = mobile
        else:
            params['mobile'] = self.get_mobile()
        if release:
            params['release'] = release
        # TODO other
        recv_count = 0
        while True:
            recv_count += 1
            web_data = requests.get(self.url, params)
            if web_data.status_code == 200:
                if web_data.text.startswith('success|'):
                    sms = web_data.text.encode(web_data.encoding).decode('utf-8')
                    print u'--> recv_sms:', sms
                    sms = sms.replace('success|', '')
                    return sms
                else:
                    print '--> explanation:', self.get_error(web_data.text)
                print '--> sleep 5s, recv_count %s' % recv_count
                time.sleep(5)
            else:
                raise Exception(u'get sms error: %s' % web_data.text)
            if recv_count >= 10:
                self.release_mobile(params['mobile'])
                raise Exception('Not recv SMS')

    def get_error(self, code):
        error_data = {
            1001: u'参数token不能为空',
            1002: u'参数action不能为空',
            1003: u'参数action错误',
            1004: u'token失效',
            1005: u'用户名或密码错误',
            1006: u'用户名不能为空',
            1007: u'密码不能为空',
            1008: u'账户余额不足',
            1009: u'账户被禁用',
            1010: u'参数错误',
            1011: u'账户待审核',
            1012: u'登录数达到上限',
            2001: u'参数itemid不能为空',
            2002: u'项目不存在',
            2003: u'项目未启用',
            2004: u'暂时没有可用的号码',
            2005: u'获取号码数量已达到上限',
            2006: u'参数mobile不能为空',
            2007: u'号码已被释放',
            2008: u'号码已离线',
            2009: u'发送内容不能为空',
            2010: u'号码正在使用中',
            3001: u'尚未收到短信',
            3002: u'等待发送',
            3003: u'正在发送',
            3004: u'发送失败',
            3005: u'订单不存在',
            3006: u'专属通道不存在',
            3007: u'专属通道未启用',
            3008: u'专属通道密码与项目不匹配',
            9001: u'系统错误',
            9002: u'系统异常',
            9003: u'系统繁忙',
        }
        return error_data.get(int(code))


if __name__ == '__main__':
    jiema = YiMa(28015)
    sms = jiema.get_sms()
    print jiema.get_sms_code(sms)
