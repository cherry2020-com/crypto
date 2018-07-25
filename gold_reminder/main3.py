#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import sys

import datetime

from utils import pusher

sys.path.extend(['/data/my_tools_env/my_tools/gold_reminder/',
                 '/data/my_tools_env/my_tools/'])
import random
import json
import os
import time

from gold_reminder.settings import GOLD_DIR
from utils.fiddler import RawToPython
from utils.send_email import Email
import urllib3


urllib3.disable_warnings()

EMAIL_RECEIVERS = [
    # '645008699@qq.com',
    # '674564128@qq.com',
]

EMAIL_RECEIVERS = set(EMAIL_RECEIVERS)


class WechatSet(object):
    FILE_PATH = os.path.join(GOLD_DIR, 'json.txt')

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


class WechatObject(object):

    def __init__(self, email_receivers=None, push_receivers=None):
        self.email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com',
                           'Gold Reminder') if email_receivers else None
        self.email_receivers = email_receivers
        self.push_receivers = push_receivers

    def test(self):
        self.send_msg('Hello, I am start !')

    def send_msg(self, msg):
        for receiver in self.email_receivers:
            self.email.send('', title=msg,
                            receiver=receiver)

        # pusher
        # for receiver in self.push_receivers:
        my_source = 's-3c91ca69-dd35-4275-9d59-5a0608fd'
        receiver_source = 'g-d22d57b4-1dda-4888-84b9-57a92766'
        url = 'com.icbc.iphoneclient://'
        content = msg,
        title = u'黄金提醒'
        sound = 'failling'
        pusher.send(my_source, receiver_source, title=title, url=url,
                    content=content, sound=sound)


class GoldMake(object):
    FD_FILE_PATH = os.path.join(GOLD_DIR, 'head', 'icbc.txt')
    LTE__CUR_MONEY_TEMP = u'低于阈值：{:.2f} 元 | '
    GTE__CUR_MONEY_TEMP = u'高于阈值：{:.2f} 元 | '
    SEP__CUR_MONEY_TEMP = u'涨浮超过：{:.2f} 元 | '
    NEW_HIGH_MONEY_TEMP = u'获得新【高】：{:.2f} 元 | '
    NEW_LOW_MONEY_TEMP = u'获得新【低】：{:.2f} 元 | '
    MONEY_TEMP = u'当前：{:.2f} 元 | {:.4f} 美元\n' \
                 u'最高：{:.2f} 元 | {:.4f} 美元\n' \
                 u'最低：{:.2f} 元 | {:.4f} 美元\n' \
                 u'涨跌：{} 元 | {} 美元\n'

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

    def get_web_data(self, name):
        web_data = self.fd_obj.requests()
        web_json = web_data.json()
        market = web_json['market']
        for each in market:
            if each['metalname'] == name:
                return each
        else:
            raise Exception('ERROR: No find icbc name in web data!!!')

    def refresh_cur_money(self):
        try:
            gold_data = self.get_web_data(u'人民币账户黄金')
            dollar_gold_data = self.get_web_data(u'美元账户黄金')
            self.cur_money = float(gold_data['middleprice'])
            self.high_money = float(gold_data['topmiddleprice'])
            self.low_money = float(gold_data['lowmiddleprice'])
            self.float_money = gold_data['openprice_dv']

            self.dollar_cur_money = float(dollar_gold_data['middleprice'])
            self.dollar_high_money = float(dollar_gold_data['topmiddleprice'])
            self.dollar_low_money = float(dollar_gold_data['lowmiddleprice'])
            self.dollar_float_money = dollar_gold_data['openprice_dv']
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
        return self.MONEY_TEMP.format(
            self.cur_money, self.dollar_cur_money,
            self.high_money, self.dollar_high_money,
            self.low_money, self.dollar_low_money,
            self.float_money, self.dollar_float_money,)

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
