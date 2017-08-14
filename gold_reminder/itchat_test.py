#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import logging
import re

import os

from gold_reminder.settings import GOLD_DIR
from utils.fiddler import RawToPython


class GoldMake(object):
    FD_FILE_PATH = os.path.join(GOLD_DIR, 'header.txt')
    LTE__CUR_MONEY_TEMP = u'低于设定阈值：{:.2f} 元\n当前价格：{:.2f} 元\n'
    GTE__CUR_MONEY_TEMP = u'高于设定阈值：{:.2f} 元\n当前价格：{:.2f} 元\n'
    SEP__CUR_MONEY_TEMP = u'涨跌浮动超过：{:.2f} 元\n当前价格：{:.2f} 元\n'
    NEW_HIGH_MONEY_TEMP = u'获得新【高】：{:.2f} 元\n'
    NEW_LOW_MONEY_TEMP = u'获得新【低】：{:.2f} 元\n'
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
                r'<dd><b>(.+?)</b><i class=".*?"></i>.*?</dd>', web_data.text) or [0]
            re_find_high = re.findall(
                r'<li>最高：(.*?)</li>'.decode('utf-8'), web_data.text) or [0]
            re_find_low = re.findall(
                r'<li class="fall">最低：<span>(.*?)</span></li>'.decode('utf-8'),
                web_data.text) or [0]
            re_find_float = re.findall(
                r'<li class="fall">涨跌额：<span>(.*?)</span></li>'.decode('utf-8'),
                web_data.text) or [0]
            self.cur_money = float(re_finds[0])
            self.high_money = float(re_find_high[0])
            self.low_money = float(re_find_low[0])
            self.float_money = float(re_find_float[0])
        except Exception as e:
            logging.error('GoldMake\n' + e)
        return self.cur_money

    def lte__cur_money(self, value):
        if value and self.cur_money:
            value = float(value)
            if self.cur_money <= value and self.lte__cur_money_tmp != value:
                self.lte__cur_money_tmp = value
                return self.LTE__CUR_MONEY_TEMP.format(value, self.cur_money)
        return ''

    def gte__cur_money(self, value):
        if value and self.cur_money:
            value = float(value)
            if self.cur_money >= value and self.gte__cur_money_tmp != value:
                self.gte__cur_money_tmp = value
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

    def new_high__cur_money(self):
        if self.tmp_high_money and self.cur_money:
            if self.tmp_high_money < self.cur_money:
                self.tmp_high_money = self.high_money
                return self.NEW_HIGH_MONEY_TEMP.format(self.cur_money)
        return ''

    def new_low__cur_money(self):
        if self.tmp_low_money and self.cur_money:
            if self.tmp_low_money > self.cur_money:
                self.tmp_low_money = self.low_money
                return self.NEW_LOW_MONEY_TEMP.format(self.cur_money)
        return ''

    def get_money_msg(self):
        return self.MONEY_TEMP.format(self.cur_money, self.high_money, self.low_money,
                                      self.float_money)

    def clear(self):
        self.lte__cur_money_tmp = 0
        self.gte__cur_money_tmp = 0

    def get_msg(self, high_value, low_value, sep_value):
        msg = self.gte__cur_money(high_value)
        msg += self.lte__cur_money(low_value)
        msg += self.sep__cur_money(sep_value)
        msg += self.new_high__cur_money()
        msg += self.new_low__cur_money()
        return msg



a = GoldMake()
print a.get_money_msg()
print a.get_msg(277, 278, 1)