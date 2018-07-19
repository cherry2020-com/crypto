#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import sys

import datetime

sys.path.extend(['/data/my_tools_env/my_tools/gold_reminder/',
                 '/data/my_tools_env/my_tools/'])
import random
import re
import json
import os
import time

from gold_reminder.settings import GOLD_DIR
from utils.fiddler import RawToPython
from utils.send_email import Email
import urllib3


urllib3.disable_warnings()

EMAIL_RECEIVERS = [
    '645008699@qq.com',
    '674564128@qq.com',
]

EMAIL_RECEIVERS = set(EMAIL_RECEIVERS)


class WechatSet(object):
    CMD_MAP = {
        u'上限': 'set_upper_func',
        u'下限': 'set_down_func',
        u'配置': 'get_setting_func',
        u'帮助': 'get_help_func',
        u'浮动': 'set_float_func',
        u'高低浮动': 'set_high_low_float_func',
        # u'调试': 'set_debug_func',
    }
    ENGLISH_CMD_MAP = {
        u'upper': 'set_upper_func',
        u'down': 'set_down_func',
        u'setting': 'get_setting_func',
        u'help': 'get_help_func',
        u'float': 'set_float_func',
        u'high low float': 'set_high_low_float_func',
        # u'debug': 'set_debug_func',
    }
    FILE_PATH = os.path.join(GOLD_DIR, 'json.txt')

    def __init__(self, msg=None):
        self.msg = msg
        self.cmds = None
        self.reverse_cmd = {}
        for cmd, cmd_fuc in self.CMD_MAP.items():
            self.reverse_cmd[cmd_fuc] = cmd

    def get_json(self):
        json_data = {}
        if os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'rb+') as fp:
                try:
                    json_data = json.load(fp, encoding='utf-8')
                except:
                    os.remove(self.FILE_PATH)
        if not os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'wb+') as fp:
                json_data = {}
                json.dump(json_data, fp, encoding='utf-8')
        return json_data

    def analysis_cmd(self):
        msg_text = self.msg.text.strip()
        if not msg_text.startswith('#'):
            return None
        if msg_text == '#':
            return GoldMake().get_money_msg() + GOLD_LINK
        self.cmds = msg_text.strip('#').split('#')
        self.cmds = [x.strip() for x in self.cmds]
        func_name = (self.CMD_MAP.get(self.cmds[0]) or
                     self.ENGLISH_CMD_MAP.get(self.cmds[0]))
        if func_name:
            try:
                return getattr(self, func_name)()
            except:
                return u'命令无法解析'
        else:
            return u'命令无法解析'

    def __save(self, update_json):
        with open(self.FILE_PATH, 'rb') as fp:
            json_data = json.load(fp, encoding='utf-8')
            json_data.update(update_json)
        with open(self.FILE_PATH, 'wb+') as fp:
            json.dump(json_data, fp, encoding='utf-8')

    def set_upper_func(self):
        json_value = float(self.cmds[1])
        json_key = (self.CMD_MAP.get(self.cmds[0]) or
                    self.ENGLISH_CMD_MAP.get(self.cmds[0]))
        update_json = {json_key: json_value}
        self.__save(update_json)
        return u'设置成功：提醒 {}：{}'.format(self.reverse_cmd[json_key], self.cmds[1])

    set_down_func = set_upper_func
    set_float_func = set_upper_func
    set_high_low_float_func = set_upper_func

    def get_setting_func(self):
        msg = u'获取配置：\n'
        for cmd_func, set_value in self.get_json().items():
            msg += u'{}：{}\n'.format(self.reverse_cmd[cmd_func], set_value)
        return msg

    def get_help_func(self):
        return u"帮助: \n" \
               u"#: 实时获取当前价格;\n" \
               u"#配置: 获取当前的配置;\n" \
               u"#上限#(数字): 上限提醒;\n" \
               u"#下限#(数字): 下限提醒;\n" \
               u"#浮动#(数字): 浮动提醒;\n" \
               u"#高低浮动#(数字): 出现新高或新低时提醒的价格浮动间隔."


class WechatObject(object):

    def __init__(self, receivers):
        self.email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com',
                           'Gold Reminder')
        self.receivers = receivers

    def test(self):
        self.send_msg('Hello, I am start !')

    def send_msg(self, msg):
        for receiver in self.receivers:
            self.email.send(GOLD_LINK, title=msg,
                            receiver=receiver)
            # print u'Send E-mail To %s: %s ...' % (receiver, msg)


class GoldMake(object):
    FD_FILE_PATH = os.path.join(GOLD_DIR, 'header.txt')
    LTE__CUR_MONEY_TEMP = u'低于阈值：{:.2f} 元 | '
    GTE__CUR_MONEY_TEMP = u'高于阈值：{:.2f} 元 | '
    SEP__CUR_MONEY_TEMP = u'涨浮超过：{:.2f} 元 | '
    NEW_HIGH_MONEY_TEMP = u'获得新【高】：{:.2f} 元 | '
    NEW_LOW_MONEY_TEMP = u'获得新【低】：{:.2f} 元 | '
    MONEY_TEMP = u'当前：{:.2f} 元\n' \
                 u'最高：{:.2f} 元\n' \
                 u'最低：{:.2f} 元\n' \
                 u'涨跌：{:.2f} 元\n'

    def __init__(self):
        self.fd_obj = RawToPython(self.FD_FILE_PATH)
        self.cur_money = 0
        self.high_money = 0
        self.low_money = 0
        self.float_money = 0
        self.refresh_cur_money()
        self.tmp_high_money = self.high_money
        self.tmp_low_money = self.low_money
        self.lte__cur_money_tmp = 0
        self.gte__cur_money_tmp = 0
        self.start_money = self.cur_money

    def refresh_cur_money(self):
        try:
            web_data = self.fd_obj.requests()
            # re_finds = re.findall(r'lineChartData.*?=(.+?);', web_data.text)
            re_finds = re.findall(
                r'<dd><b.*?>(.+?)</b><i class=".*?"></i>.*?</dd>',
                web_data.text) or [0]
            re_find_high = re.findall(
                r'<li.*?>最高：.*?(\d+\.\d+).*?<\/li.*?>'.decode('utf-8'),
                web_data.text) or [0]
            re_find_low = re.findall(
                r'<li.*?>最低：<span>(.*?)</span></li>'.decode('utf-8'),
                web_data.text) or [0]
            re_find_float = re.findall(
                r'<li.*?>涨跌额：<span>(.*?)</span></li>'.decode('utf-8'),
                web_data.text) or [0]
            self.cur_money = float(re_finds[0])
            self.high_money = float(re_find_high[0])
            self.low_money = float(re_find_low[0])
            self.float_money = float(re_find_float[0])
        except Exception as e:
            pass
        return self.cur_money

    def lte__cur_money(self, value):
        if value and self.cur_money:
            value = float(value)
            if self.cur_money <= value and self.lte__cur_money_tmp != self.cur_money:
                self.lte__cur_money_tmp = self.cur_money
                return self.LTE__CUR_MONEY_TEMP.format(value, self.cur_money)
        return ''

    def gte__cur_money(self, value):
        if value and self.cur_money:
            value = float(value)
            if self.cur_money >= value and self.gte__cur_money_tmp != self.cur_money:
                self.gte__cur_money_tmp = self.cur_money
                return self.GTE__CUR_MONEY_TEMP.format(value, self.cur_money)
        return ''

    def sep__cur_money(self, value):
        if value and self.start_money and self.cur_money:
            value = float(value)
            sep_money = abs(self.start_money - self.cur_money) - value
            if sep_money >= 0:
                self.start_money = self.cur_money
                return self.SEP__CUR_MONEY_TEMP.format(value, self.cur_money)
        return ''

    def new_high__cur_money(self, high_low_sep_value):
        if self.tmp_high_money and self.cur_money:
            if self.tmp_high_money < self.cur_money:
                if high_low_sep_value:
                    high_low_sep_value = float(high_low_sep_value)
                    if (self.cur_money - self.tmp_high_money) >= high_low_sep_value:
                        self.tmp_high_money = self.high_money
                        return self.NEW_HIGH_MONEY_TEMP.format(self.cur_money)
                else:
                    self.tmp_high_money = self.high_money
                    return self.NEW_HIGH_MONEY_TEMP.format(self.cur_money)
        return ''

    def new_low__cur_money(self, high_low_sep_value):
        if self.tmp_low_money and self.cur_money:
            if self.tmp_low_money > self.cur_money:
                if high_low_sep_value:
                    high_low_sep_value = float(high_low_sep_value)
                    if (self.tmp_low_money - self.cur_money) >= high_low_sep_value:
                        self.tmp_low_money = self.low_money
                        return self.NEW_LOW_MONEY_TEMP.format(self.cur_money)
                else:
                    self.tmp_low_money = self.low_money
                    return self.NEW_LOW_MONEY_TEMP.format(self.cur_money)
        return ''

    def get_money_msg(self):
        return self.MONEY_TEMP.format(self.cur_money, self.high_money, self.low_money,
                                      self.float_money)

    def clear(self):
        self.lte__cur_money_tmp = 0
        self.gte__cur_money_tmp = 0

    def get_msg(self, high_value, low_value, sep_value, high_low_sep_value):
        msg = self.gte__cur_money(high_value)
        msg += self.lte__cur_money(low_value)
        msg += self.sep__cur_money(sep_value)
        msg += self.new_high__cur_money(high_low_sep_value)
        msg += self.new_low__cur_money(high_low_sep_value)
        if msg:
            msg += self.get_money_msg()
        return msg

GOLD_LINK = u'\nhttp://t.cn/R9BAmdm'

def do_while():
    print '%s: start' % datetime.datetime.now()
    itchat_obj = WechatObject(EMAIL_RECEIVERS)
    # itchat_obj.test()
    make_obj = GoldMake()
    set_obj = WechatSet()
    itchat_obj.send_msg(make_obj.get_money_msg())
    next_time = 0
    clear_time = 0
    msg = ''
    while True:
        now_time = int(time.time())
        if next_time < now_time:
            print ''
            json_data = set_obj.get_json()
            make_obj.refresh_cur_money()
            msg = make_obj.get_msg(json_data.get('set_upper_func'),
                                   json_data.get('set_down_func'),
                                   json_data.get('set_float_func'),
                                   json_data.get('set_high_low_float_func'))
            if msg:
                print '%s: send msg.' % datetime.datetime.now()
                itchat_obj.send_msg(msg)
            next_time = now_time + random.randint(1, 5)
            sys.stdout.flush()
        if clear_time < now_time:
            clear_time = now_time + 600
            make_obj.clear()
        time.sleep(1)
        print ',',


if __name__ == '__main__':
    do_while()
