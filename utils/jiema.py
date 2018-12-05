#!/usr/bin/python
# -*- coding: UTF-8 -*-
import logging
import re
from urllib import quote

import requests
import time

from utils import settings


class YiMaError(Exception):
    pass


class YiMa(object):
    """
    http://www.51ym.me/User/apidocs.html
    """

    def __init__(self, item_id, token='0101454744924a6c4188dfeed50390c0a54c609c1d01',
                 wait_count=10, wait_time=3, request_timeout=5):
        """

        :param item_id: 项目编号   项目对应的数字编号
        :param token: 令牌	登录接口获取的token值
        :param sms_wait_count: 等待次数 - 获取短信的等待次数
        :param sms_wait_time: 每次等待时间 单位秒
        :param request_timeout: 请求超时时间 单位秒
        """
        self.url = 'http://api.fxhyd.cn/UserInterface.aspx'
        self._token = token
        self.item_id = item_id
        self._is_release_mobile = True
        self._wait_count = wait_count
        self._wait_time = wait_time
        self._request_timeout = request_timeout
        self._excludeno = ''

    def send_sms(self, mobile, sms):
        """

        :param mobile: (int) 手机号码 - 要获取短信的手机号码。
        :param sms: (str) 发送内容 - 要发送的短信内容
        :return: None
        """
        params = {'action': 'sendsms', 'token': self._token,
                  'itemid': self.item_id, 'mobile': mobile, 'sms': quote(sms)}
        # 请求数据
        web_data = requests.get(self.url, params, timeout=self._request_timeout)
        had_wait_count = 0
        if web_data.status_code == 200:
            if web_data.text.startswith('success'):
                logging.info(u'发送短信命令 成功: {}'.format(sms))
                while True:
                    if self._send_sms_result(mobile):
                        break
                    logging.info(u'短信发送结果 重试, {}秒后将重新查询, 已等待次数: {}/{}'.format(
                        self._wait_time, had_wait_count, self._wait_count))
                    time.sleep(self._wait_time)
                    had_wait_count += 1
                    if had_wait_count > self._wait_count:
                        tmp_msg = u'短信发送结果 重试次数达到上限: {}'.format(
                            self._wait_count)
                        logging.error(tmp_msg)
                        raise YiMaError(tmp_msg)
            else:
                tmp_msg = u'发送短信命令 失败: {}'.format(self._get_error(web_data.text))
                logging.error(tmp_msg)
                raise YiMaError(tmp_msg)
        else:
            tmp_msg = u'发送短信命令 请求失败: {}'.format(web_data.status_code)
            logging.error(tmp_msg)
            raise YiMaError(tmp_msg)

    def _send_sms_result(self, mobile):
        params = {'action': 'getsendsmsstate', 'token': self._token,
                  'itemid': self.item_id, 'mobile': mobile}
        # 请求数据
        web_data = requests.get(self.url, params, timeout=self._request_timeout)
        if web_data.status_code == 200:
            if web_data.text.startswith('success'):
                logging.info(u'短信发送结果 成功')
                return True
            else:
                tmp_msg = u'短信发送结果 异常: {}'.format(self._get_error(web_data.text))
                logging.exception(tmp_msg)
        else:
            tmp_msg = u'短信发送结果 请求失败: {}'.format(web_data.status_code)
            logging.error(tmp_msg)
            raise YiMaError(tmp_msg)

    def add_exclude_segment(self, segments):
        """
        添加排除的号段
        :param segment: (int) 号码的号段 - eg. 170、171、188
        :return: None
        """
        if self._excludeno:
            self._excludeno += '.'
        if isinstance(segments, int):
            self._excludeno += str(segments)
        else:
            self._excludeno += '.'.join([str(x) for x in segments])

    def get_mobile(self, isp=None, province_city=None,
                   mobile=None):
        """

        :param isp:(int) 运营商代码 - 号码所属运营商代码。1:移动，2:联通，3:电信
        :param province_city:(str) 省/省市 - 号码归属地的省份，省市 eg.辽宁省, 辽宁省大连市
        :param mobile:(int) 指定号码	要指定获取的号码，该号码必须是本平台的号码。
        :return: 返回手机号
        """
        # 设置参数
        params = {'action': 'getmobile', 'token': self._token,
                  'itemid': self.item_id}
        if province_city:
            province, city = self._get_province_city_code(province_city)
            if province:
                params['province'] = province
            if city:
                params['city'] = city
        if isp:
            params['isp'] = isp
        if mobile:
            params['mobile'] = mobile
        if self._excludeno:
            params['excludeno'] = self._excludeno

        # 请求数据
        web_data = requests.get(self.url, params)
        if web_data.status_code == 200:
            if web_data.text.startswith('success'):
                mobile = web_data.text.replace('success|', '')
                if not mobile.isalnum():
                    tmp_msg = u'获取手机号 失败: {}'.format(mobile)
                    logging.error(tmp_msg)
                    raise YiMaError(tmp_msg)
                self._is_release_mobile = False
                logging.info(u'获取到手机号 成功: {}'.format(mobile))
                return mobile
            else:
                tmp_msg = u'获取手机号 失败: {}'.format(self._get_error(web_data.text))
                logging.error(tmp_msg)
                raise YiMaError(tmp_msg)
        tmp_msg = u'获取手机号失败: {}'.format(web_data.text)
        logging.error(tmp_msg)
        raise YiMaError(tmp_msg)

    def release_mobile(self, mobile):
        if self._is_release_mobile:
            logging.info(u'手机号已经释放，不需要再次释放')
            return
        params = {'action': 'release', 'token': self._token,
                  'itemid': self.item_id, 'mobile': mobile}
        web_data = requests.get(self.url, params)
        if web_data.status_code == 200:
            if web_data.text.startswith('success'):
                logging.info(u'释放手机号成功')
            else:
                logging.exception(u'释放手机号异常: {}'.format(
                    self._get_error(web_data.text)))
            self._is_release_mobile = True
        else:
            tmp_msg = u'释放手机号请求失败: {}'.format(web_data.status_code)
            logging.error(tmp_msg)
            raise YiMaError(tmp_msg)

    def get_sms(self, mobile, release=1, getsendno=None, sms_pattern=r'\d{4,6}'):
        """
        获取短信
        :param mobile: 手机号码 - 要获取短信的手机号码。
        :param release: 自动释放号码标识符 - 若该参数值为1时，获取到短信的同时系统将自己释放该手机号码。
                                          若要继续使用该号码，请勿带入该参数。
        :param getsendno: 是否返回发送号码 - 若该参数值为1时，则将短信发送号码附加在短信最后用#分隔。
        :param sms_pattern: 正则表达式 - 返回 获取短信内容的正则匹配后的结果
        :return: 短信内容 - 受sms_pattern参数影响
        """
        params = {'action': 'getsms', 'token': self._token,
                  'itemid': self.item_id, 'mobile': mobile}
        if release:
            params['release'] = release
        if getsendno:
            params['getsendno'] = getsendno
        recv_count = 0
        while True:
            recv_count += 1
            web_data = requests.get(self.url, params)
            if web_data.status_code == 200:
                if web_data.text.startswith('success|'):
                    sms = web_data.text.encode(web_data.encoding).decode('utf-8')
                    logging.info(u'获取到短信内容: {}'.format(sms))
                    sms = sms.replace('success|', '')
                    if sms_pattern:
                        codes = re.findall(sms_pattern, sms)
                        if len(codes) == 1:
                            logging.info(u'正则匹配结果: {}'.format(codes[0]))
                            return codes[0]
                        tmp_msg = u"正则匹配后无结果: {}".format(sms)
                        logging.error(tmp_msg)
                        raise YiMaError(tmp_msg)
                    return sms
                else:
                    error_msg = self._get_error(web_data.text)
                    if error_msg:
                        tmp_msg = u'获取短信内容异常: {}'.format(error_msg)
                        logging.exception(tmp_msg)
                        raise YiMaError(tmp_msg)
                logging.info(u'未收到短信内容, {}秒后将重新查询, 已等待次数: {}/{}'.format(
                    self._wait_time, recv_count, self._wait_count))
                time.sleep(self._wait_time)
            else:
                tmp_msg = u'获取短信内容网络请求失败: {}'.format(web_data.status_code)
                logging.exception(tmp_msg)
                raise YiMaError(tmp_msg)
            if recv_count >= self._wait_count:
                tmp_msg = u'等待短信内容次数达到上限({}), 手机号将释放'.format(
                    self._wait_count)
                logging.exception(tmp_msg)
                self.release_mobile(params['mobile'])
                raise YiMaError(tmp_msg)

    def _get_error(self, code):
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
        no_error_codes = {3001}
        code = int(code)
        if code in no_error_codes:
            return None
        return error_data.get(code)

    def _get_province_city_code(self, province_city):
        """
        :param province_city: 省市 - eg. 辽宁省-大连市
        :return: 省市编码
        """

        provinces = [
            {
                "AreaType": 1,
                "AreaCode": 110000,
                "AreaName": "北京市",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 110101,
                        "AreaName": "东城区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110102,
                        "AreaName": "西城区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110105,
                        "AreaName": "朝阳区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110106,
                        "AreaName": "丰台区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110107,
                        "AreaName": "石景山区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110108,
                        "AreaName": "海淀区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110109,
                        "AreaName": "门头沟区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110111,
                        "AreaName": "房山区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110112,
                        "AreaName": "通州区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110113,
                        "AreaName": "顺义区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110114,
                        "AreaName": "昌平区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110115,
                        "AreaName": "大兴区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110116,
                        "AreaName": "怀柔区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110117,
                        "AreaName": "平谷区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110228,
                        "AreaName": "密云县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 110229,
                        "AreaName": "延庆县",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 120000,
                "AreaName": "天津市",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 120101,
                        "AreaName": "和平区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120102,
                        "AreaName": "河东区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120103,
                        "AreaName": "河西区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120104,
                        "AreaName": "南开区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120105,
                        "AreaName": "河北区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120106,
                        "AreaName": "红桥区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120110,
                        "AreaName": "东丽区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120111,
                        "AreaName": "西青区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120112,
                        "AreaName": "津南区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120113,
                        "AreaName": "北辰区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120114,
                        "AreaName": "武清区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120115,
                        "AreaName": "宝坻区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120116,
                        "AreaName": "滨海新区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120221,
                        "AreaName": "宁河县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120223,
                        "AreaName": "静海县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 120225,
                        "AreaName": "蓟县",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 130000,
                "AreaName": "河北省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 130100,
                        "AreaName": "石家庄市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 130200,
                        "AreaName": "唐山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 130300,
                        "AreaName": "秦皇岛市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 130400,
                        "AreaName": "邯郸市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 130500,
                        "AreaName": "邢台市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 130600,
                        "AreaName": "保定市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 130700,
                        "AreaName": "张家口市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 130800,
                        "AreaName": "承德市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 130900,
                        "AreaName": "沧州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 131000,
                        "AreaName": "廊坊市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 131100,
                        "AreaName": "衡水市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 140000,
                "AreaName": "山西省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 140100,
                        "AreaName": "太原市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 140200,
                        "AreaName": "大同市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 140300,
                        "AreaName": "阳泉市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 140400,
                        "AreaName": "长治市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 140500,
                        "AreaName": "晋城市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 140600,
                        "AreaName": "朔州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 140700,
                        "AreaName": "晋中市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 140800,
                        "AreaName": "运城市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 140900,
                        "AreaName": "忻州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 141000,
                        "AreaName": "临汾市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 141100,
                        "AreaName": "吕梁市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 150000,
                "AreaName": "内蒙古自治区",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 150100,
                        "AreaName": "呼和浩特市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 150200,
                        "AreaName": "包头市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 150300,
                        "AreaName": "乌海市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 150400,
                        "AreaName": "赤峰市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 150500,
                        "AreaName": "通辽市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 150600,
                        "AreaName": "鄂尔多斯市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 150700,
                        "AreaName": "呼伦贝尔市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 150800,
                        "AreaName": "巴彦淖尔市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 150900,
                        "AreaName": "乌兰察布市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 152200,
                        "AreaName": "兴安盟",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 152500,
                        "AreaName": "锡林郭勒盟",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 152900,
                        "AreaName": "阿拉善盟",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 210000,
                "AreaName": "辽宁省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 210100,
                        "AreaName": "沈阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 210200,
                        "AreaName": "大连市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 210300,
                        "AreaName": "鞍山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 210400,
                        "AreaName": "抚顺市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 210500,
                        "AreaName": "本溪市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 210600,
                        "AreaName": "丹东市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 210700,
                        "AreaName": "锦州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 210800,
                        "AreaName": "营口市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 210900,
                        "AreaName": "阜新市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 211000,
                        "AreaName": "辽阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 211100,
                        "AreaName": "盘锦市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 211200,
                        "AreaName": "铁岭市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 211300,
                        "AreaName": "朝阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 211400,
                        "AreaName": "葫芦岛市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 220000,
                "AreaName": "吉林省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 220100,
                        "AreaName": "长春市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 220200,
                        "AreaName": "吉林市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 220300,
                        "AreaName": "四平市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 220400,
                        "AreaName": "辽源市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 220500,
                        "AreaName": "通化市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 220600,
                        "AreaName": "白山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 220700,
                        "AreaName": "松原市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 220800,
                        "AreaName": "白城市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 222400,
                        "AreaName": "延边朝鲜族自治州",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 230000,
                "AreaName": "黑龙江省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 230100,
                        "AreaName": "哈尔滨市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 230200,
                        "AreaName": "齐齐哈尔市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 230300,
                        "AreaName": "鸡西市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 230400,
                        "AreaName": "鹤岗市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 230500,
                        "AreaName": "双鸭山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 230600,
                        "AreaName": "大庆市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 230700,
                        "AreaName": "伊春市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 230800,
                        "AreaName": "佳木斯市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 230900,
                        "AreaName": "七台河市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 231000,
                        "AreaName": "牡丹江市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 231100,
                        "AreaName": "黑河市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 231200,
                        "AreaName": "绥化市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 232700,
                        "AreaName": "大兴安岭地区",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 310000,
                "AreaName": "上海市",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 310101,
                        "AreaName": "黄浦区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310104,
                        "AreaName": "徐汇区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310105,
                        "AreaName": "长宁区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310106,
                        "AreaName": "静安区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310107,
                        "AreaName": "普陀区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310108,
                        "AreaName": "闸北区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310109,
                        "AreaName": "虹口区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310110,
                        "AreaName": "杨浦区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310112,
                        "AreaName": "闵行区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310113,
                        "AreaName": "宝山区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310114,
                        "AreaName": "嘉定区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310115,
                        "AreaName": "浦东新区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310116,
                        "AreaName": "金山区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310117,
                        "AreaName": "松江区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310118,
                        "AreaName": "青浦区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310120,
                        "AreaName": "奉贤区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 310230,
                        "AreaName": "崇明县",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 320000,
                "AreaName": "江苏省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 320100,
                        "AreaName": "南京市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 320200,
                        "AreaName": "无锡市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 320300,
                        "AreaName": "徐州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 320400,
                        "AreaName": "常州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 320500,
                        "AreaName": "苏州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 320600,
                        "AreaName": "南通市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 320700,
                        "AreaName": "连云港市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 320800,
                        "AreaName": "淮安市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 320900,
                        "AreaName": "盐城市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 321000,
                        "AreaName": "扬州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 321100,
                        "AreaName": "镇江市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 321200,
                        "AreaName": "泰州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 321300,
                        "AreaName": "宿迁市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 330000,
                "AreaName": "浙江省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 330100,
                        "AreaName": "杭州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 330200,
                        "AreaName": "宁波市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 330300,
                        "AreaName": "温州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 330400,
                        "AreaName": "嘉兴市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 330500,
                        "AreaName": "湖州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 330600,
                        "AreaName": "绍兴市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 330700,
                        "AreaName": "金华市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 330800,
                        "AreaName": "衢州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 330900,
                        "AreaName": "舟山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 331000,
                        "AreaName": "台州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 331100,
                        "AreaName": "丽水市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 340000,
                "AreaName": "安徽省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 340100,
                        "AreaName": "合肥市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 340200,
                        "AreaName": "芜湖市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 340300,
                        "AreaName": "蚌埠市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 340400,
                        "AreaName": "淮南市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 340500,
                        "AreaName": "马鞍山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 340600,
                        "AreaName": "淮北市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 340700,
                        "AreaName": "铜陵市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 340800,
                        "AreaName": "安庆市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 341000,
                        "AreaName": "黄山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 341100,
                        "AreaName": "滁州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 341200,
                        "AreaName": "阜阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 341300,
                        "AreaName": "宿州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 341500,
                        "AreaName": "六安市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 341600,
                        "AreaName": "亳州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 341700,
                        "AreaName": "池州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 341800,
                        "AreaName": "宣城市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 350000,
                "AreaName": "福建省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 350100,
                        "AreaName": "福州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 350200,
                        "AreaName": "厦门市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 350300,
                        "AreaName": "莆田市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 350400,
                        "AreaName": "三明市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 350500,
                        "AreaName": "泉州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 350600,
                        "AreaName": "漳州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 350700,
                        "AreaName": "南平市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 350800,
                        "AreaName": "龙岩市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 350900,
                        "AreaName": "宁德市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 360000,
                "AreaName": "江西省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 360100,
                        "AreaName": "南昌市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 360200,
                        "AreaName": "景德镇市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 360300,
                        "AreaName": "萍乡市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 360400,
                        "AreaName": "九江市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 360500,
                        "AreaName": "新余市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 360600,
                        "AreaName": "鹰潭市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 360700,
                        "AreaName": "赣州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 360800,
                        "AreaName": "吉安市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 360900,
                        "AreaName": "宜春市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 361000,
                        "AreaName": "抚州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 361100,
                        "AreaName": "上饶市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 370000,
                "AreaName": "山东省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 370100,
                        "AreaName": "济南市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 370200,
                        "AreaName": "青岛市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 370300,
                        "AreaName": "淄博市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 370400,
                        "AreaName": "枣庄市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 370500,
                        "AreaName": "东营市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 370600,
                        "AreaName": "烟台市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 370700,
                        "AreaName": "潍坊市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 370800,
                        "AreaName": "济宁市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 370900,
                        "AreaName": "泰安市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 371000,
                        "AreaName": "威海市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 371100,
                        "AreaName": "日照市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 371200,
                        "AreaName": "莱芜市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 371300,
                        "AreaName": "临沂市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 371400,
                        "AreaName": "德州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 371500,
                        "AreaName": "聊城市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 371600,
                        "AreaName": "滨州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 371700,
                        "AreaName": "菏泽市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 410000,
                "AreaName": "河南省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 410100,
                        "AreaName": "郑州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 410200,
                        "AreaName": "开封市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 410300,
                        "AreaName": "洛阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 410400,
                        "AreaName": "平顶山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 410500,
                        "AreaName": "安阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 410600,
                        "AreaName": "鹤壁市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 410700,
                        "AreaName": "新乡市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 410800,
                        "AreaName": "焦作市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 410900,
                        "AreaName": "濮阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 411000,
                        "AreaName": "许昌市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 411100,
                        "AreaName": "漯河市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 411200,
                        "AreaName": "三门峡市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 411300,
                        "AreaName": "南阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 411400,
                        "AreaName": "商丘市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 411500,
                        "AreaName": "信阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 411600,
                        "AreaName": "周口市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 411700,
                        "AreaName": "驻马店市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 419000,
                        "AreaName": "省直辖县级行政区划",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 420000,
                "AreaName": "湖北省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 420100,
                        "AreaName": "武汉市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 420200,
                        "AreaName": "黄石市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 420300,
                        "AreaName": "十堰市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 420500,
                        "AreaName": "宜昌市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 420600,
                        "AreaName": "襄阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 420700,
                        "AreaName": "鄂州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 420800,
                        "AreaName": "荆门市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 420900,
                        "AreaName": "孝感市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 421000,
                        "AreaName": "荆州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 421100,
                        "AreaName": "黄冈市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 421200,
                        "AreaName": "咸宁市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 421300,
                        "AreaName": "随州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 422800,
                        "AreaName": "恩施土家族苗族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 429000,
                        "AreaName": "省直辖县级行政区划",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 430000,
                "AreaName": "湖南省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 430100,
                        "AreaName": "长沙市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 430200,
                        "AreaName": "株洲市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 430300,
                        "AreaName": "湘潭市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 430400,
                        "AreaName": "衡阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 430500,
                        "AreaName": "邵阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 430600,
                        "AreaName": "岳阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 430700,
                        "AreaName": "常德市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 430800,
                        "AreaName": "张家界市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 430900,
                        "AreaName": "益阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 431000,
                        "AreaName": "郴州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 431100,
                        "AreaName": "永州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 431200,
                        "AreaName": "怀化市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 431300,
                        "AreaName": "娄底市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 433100,
                        "AreaName": "湘西土家族苗族自治州",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 440000,
                "AreaName": "广东省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 440100,
                        "AreaName": "广州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 440200,
                        "AreaName": "韶关市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 440300,
                        "AreaName": "深圳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 440400,
                        "AreaName": "珠海市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 440500,
                        "AreaName": "汕头市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 440600,
                        "AreaName": "佛山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 440700,
                        "AreaName": "江门市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 440800,
                        "AreaName": "湛江市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 440900,
                        "AreaName": "茂名市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 441200,
                        "AreaName": "肇庆市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 441300,
                        "AreaName": "惠州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 441400,
                        "AreaName": "梅州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 441500,
                        "AreaName": "汕尾市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 441600,
                        "AreaName": "河源市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 441700,
                        "AreaName": "阳江市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 441800,
                        "AreaName": "清远市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 441900,
                        "AreaName": "东莞市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 442000,
                        "AreaName": "中山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 445100,
                        "AreaName": "潮州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 445200,
                        "AreaName": "揭阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 445300,
                        "AreaName": "云浮市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 450000,
                "AreaName": "广西壮族自治区",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 450100,
                        "AreaName": "南宁市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 450200,
                        "AreaName": "柳州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 450300,
                        "AreaName": "桂林市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 450400,
                        "AreaName": "梧州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 450500,
                        "AreaName": "北海市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 450600,
                        "AreaName": "防城港市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 450700,
                        "AreaName": "钦州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 450800,
                        "AreaName": "贵港市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 450900,
                        "AreaName": "玉林市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 451000,
                        "AreaName": "百色市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 451100,
                        "AreaName": "贺州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 451200,
                        "AreaName": "河池市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 451300,
                        "AreaName": "来宾市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 451400,
                        "AreaName": "崇左市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 460000,
                "AreaName": "海南省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 460100,
                        "AreaName": "海口市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 460200,
                        "AreaName": "三亚市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 460300,
                        "AreaName": "三沙市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 469000,
                        "AreaName": "省直辖县级行政区划",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 500000,
                "AreaName": "重庆市",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 500101,
                        "AreaName": "万州区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500102,
                        "AreaName": "涪陵区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500103,
                        "AreaName": "渝中区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500104,
                        "AreaName": "大渡口区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500105,
                        "AreaName": "江北区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500106,
                        "AreaName": "沙坪坝区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500107,
                        "AreaName": "九龙坡区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500108,
                        "AreaName": "南岸区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500109,
                        "AreaName": "北碚区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500110,
                        "AreaName": "綦江区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500111,
                        "AreaName": "大足区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500112,
                        "AreaName": "渝北区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500113,
                        "AreaName": "巴南区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500114,
                        "AreaName": "黔江区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500115,
                        "AreaName": "长寿区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500116,
                        "AreaName": "江津区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500117,
                        "AreaName": "合川区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500118,
                        "AreaName": "永川区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500119,
                        "AreaName": "南川区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500120,
                        "AreaName": "璧山区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500151,
                        "AreaName": "铜梁区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500223,
                        "AreaName": "潼南县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500226,
                        "AreaName": "荣昌县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500228,
                        "AreaName": "梁平县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500229,
                        "AreaName": "城口县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500230,
                        "AreaName": "丰都县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500231,
                        "AreaName": "垫江县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500232,
                        "AreaName": "武隆县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500233,
                        "AreaName": "忠县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500234,
                        "AreaName": "开县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500235,
                        "AreaName": "云阳县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500236,
                        "AreaName": "奉节县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500237,
                        "AreaName": "巫山县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500238,
                        "AreaName": "巫溪县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500240,
                        "AreaName": "石柱土家族自治县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500241,
                        "AreaName": "秀山土家族苗族自治县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500242,
                        "AreaName": "酉阳土家族苗族自治县",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 500243,
                        "AreaName": "彭水苗族土家族自治县",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 510000,
                "AreaName": "四川省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 510100,
                        "AreaName": "成都市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 510300,
                        "AreaName": "自贡市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 510400,
                        "AreaName": "攀枝花市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 510500,
                        "AreaName": "泸州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 510600,
                        "AreaName": "德阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 510700,
                        "AreaName": "绵阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 510800,
                        "AreaName": "广元市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 510900,
                        "AreaName": "遂宁市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511000,
                        "AreaName": "内江市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511100,
                        "AreaName": "乐山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511300,
                        "AreaName": "南充市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511400,
                        "AreaName": "眉山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511500,
                        "AreaName": "宜宾市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511600,
                        "AreaName": "广安市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511700,
                        "AreaName": "达州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511800,
                        "AreaName": "雅安市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 511900,
                        "AreaName": "巴中市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 512000,
                        "AreaName": "资阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 513200,
                        "AreaName": "阿坝藏族羌族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 513300,
                        "AreaName": "甘孜藏族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 513400,
                        "AreaName": "凉山彝族自治州",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 520000,
                "AreaName": "贵州省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 520100,
                        "AreaName": "贵阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 520200,
                        "AreaName": "六盘水市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 520300,
                        "AreaName": "遵义市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 520400,
                        "AreaName": "安顺市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 520500,
                        "AreaName": "毕节市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 520600,
                        "AreaName": "铜仁市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 522300,
                        "AreaName": "黔西南布依族苗族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 522600,
                        "AreaName": "黔东南苗族侗族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 522700,
                        "AreaName": "黔南布依族苗族自治州",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 530000,
                "AreaName": "云南省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 530100,
                        "AreaName": "昆明市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 530300,
                        "AreaName": "曲靖市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 530400,
                        "AreaName": "玉溪市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 530500,
                        "AreaName": "保山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 530600,
                        "AreaName": "昭通市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 530700,
                        "AreaName": "丽江市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 530800,
                        "AreaName": "普洱市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 530900,
                        "AreaName": "临沧市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 532300,
                        "AreaName": "楚雄彝族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 532500,
                        "AreaName": "红河哈尼族彝族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 532600,
                        "AreaName": "文山壮族苗族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 532800,
                        "AreaName": "西双版纳傣族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 532900,
                        "AreaName": "大理白族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 533100,
                        "AreaName": "德宏傣族景颇族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 533300,
                        "AreaName": "怒江傈僳族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 533400,
                        "AreaName": "迪庆藏族自治州",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 540000,
                "AreaName": "西藏自治区",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 540100,
                        "AreaName": "拉萨市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 540200,
                        "AreaName": "日喀则市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 542100,
                        "AreaName": "昌都地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 542200,
                        "AreaName": "山南地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 542400,
                        "AreaName": "那曲地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 542500,
                        "AreaName": "阿里地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 542600,
                        "AreaName": "林芝地区",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 610000,
                "AreaName": "陕西省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 610100,
                        "AreaName": "西安市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 610200,
                        "AreaName": "铜川市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 610300,
                        "AreaName": "宝鸡市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 610400,
                        "AreaName": "咸阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 610500,
                        "AreaName": "渭南市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 610600,
                        "AreaName": "延安市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 610700,
                        "AreaName": "汉中市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 610800,
                        "AreaName": "榆林市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 610900,
                        "AreaName": "安康市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 611000,
                        "AreaName": "商洛市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 620000,
                "AreaName": "甘肃省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 620100,
                        "AreaName": "兰州市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 620200,
                        "AreaName": "嘉峪关市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 620300,
                        "AreaName": "金昌市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 620400,
                        "AreaName": "白银市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 620500,
                        "AreaName": "天水市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 620600,
                        "AreaName": "武威市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 620700,
                        "AreaName": "张掖市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 620800,
                        "AreaName": "平凉市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 620900,
                        "AreaName": "酒泉市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 621000,
                        "AreaName": "庆阳市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 621100,
                        "AreaName": "定西市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 621200,
                        "AreaName": "陇南市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 622900,
                        "AreaName": "临夏回族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 623000,
                        "AreaName": "甘南藏族自治州",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 630000,
                "AreaName": "青海省",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 630100,
                        "AreaName": "西宁市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 630200,
                        "AreaName": "海东市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 632200,
                        "AreaName": "海北藏族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 632300,
                        "AreaName": "黄南藏族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 632500,
                        "AreaName": "海南藏族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 632600,
                        "AreaName": "果洛藏族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 632700,
                        "AreaName": "玉树藏族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 632800,
                        "AreaName": "海西蒙古族藏族自治州",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 640000,
                "AreaName": "宁夏回族自治区",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 640100,
                        "AreaName": "银川市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 640200,
                        "AreaName": "石嘴山市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 640300,
                        "AreaName": "吴忠市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 640400,
                        "AreaName": "固原市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 640500,
                        "AreaName": "中卫市",
                        "Children": [

                        ]
                    }
                ]
            },
            {
                "AreaType": 1,
                "AreaCode": 650000,
                "AreaName": "新疆维吾尔自治区",
                "Children": [
                    {
                        "AreaType": 2,
                        "AreaCode": 650100,
                        "AreaName": "乌鲁木齐市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 650200,
                        "AreaName": "克拉玛依市",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 652100,
                        "AreaName": "吐鲁番地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 652200,
                        "AreaName": "哈密地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 652300,
                        "AreaName": "昌吉回族自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 652700,
                        "AreaName": "博尔塔拉蒙古自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 652800,
                        "AreaName": "巴音郭楞蒙古自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 652900,
                        "AreaName": "阿克苏地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 653000,
                        "AreaName": "克孜勒苏柯尔克孜自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 653100,
                        "AreaName": "喀什地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 653200,
                        "AreaName": "和田地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 654000,
                        "AreaName": "伊犁哈萨克自治州",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 654200,
                        "AreaName": "塔城地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 654300,
                        "AreaName": "阿勒泰地区",
                        "Children": [

                        ]
                    },
                    {
                        "AreaType": 2,
                        "AreaCode": 659000,
                        "AreaName": "自治区直辖县级行政区划",
                        "Children": [

                        ]
                    }
                ]
            }
        ]

        code_map = {}
        for p in provinces:
            code_map[p['AreaName'].decode('utf-8')] = (p['AreaCode'], None)
            for c in p['Children']:
                code_map[p['AreaName'].decode('utf-8') +
                         c['AreaName'].decode('utf-8')] = (p['AreaCode'], c['AreaCode'])
                assert not c['Children']
        if province_city not in code_map:
            raise YiMaError(u'No Find Province-City: %s' % province_city)
        return code_map[province_city]


if __name__ == '__main__':
    jiema = YiMa(15585)
    jiema.add_exclude_segment(170)
    mobile = jiema.get_mobile(1, u'辽宁省大连市')
    print jiema.get_sms(mobile)
