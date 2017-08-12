#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import re

import itchat
import json

import os

import time

from gold_reminder.settings import GOLD_DIR
from utils.fiddler import RawToPython

import urllib3
urllib3.disable_warnings()


@itchat.msg_register(itchat.content.TEXT, isFriendChat=True,
                     isGroupChat=True, isMpChat=True)
def text_reply(msg):
    if msg.get('User') and msg.get('User').get('NickName').startswith(u'黄金'):
        return WechatSet(msg).analysis_cmd()
    return u'本服务不支持您，欢迎联系管理员 ~'


class WechatSet(object):
    CMD_MAP = {
        u'上限': 'set_upper_func',
        u'下限': 'set_down_func'
    }
    FILE_PATH = os.path.join(GOLD_DIR, 'json.txt')

    def __init__(self, msg=None):
        self.msg = msg
        self.cmds = None

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
            return CUR_MONEY_TEMP.format(GoldMake().cur_money) + GOLD_LINK
        self.cmds = msg_text.strip('#').split('#')
        self.cmds = [x.strip() for x in self.cmds]
        func_name = self.CMD_MAP.get(self.cmds[0])
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
        value = float(self.cmds[1])
        update_json = {self.CMD_MAP[self.cmds[0]]: value}
        self.__save(update_json)
        return u'设置成功：提醒 {}：{}'.format(self.cmds[0], self.cmds[1])

    set_down_func = set_upper_func


class WechatObject(object):

    def __init__(self, enable_cmd_qr=False):
        itchat.auto_login(enableCmdQR=enable_cmd_qr, hotReload=True)
        itchat.send('Hello, I am start !', toUserName='filehelper')
        self.gold_rooms = itchat.search_chatrooms(name=u'黄金')

    def test(self):
        self.send_msg('Hello, I am start !')

    def send_msg(self, msg):
        for gold_room in self.gold_rooms:
            gold_room_name = gold_room['UserName']
            msg += GOLD_LINK
            itchat.send(msg, toUserName=gold_room_name)

    def run(self, block_thread=False):
        itchat.run(blockThread=block_thread)


class GoldMake(object):
    FD_FILE_PATH = os.path.join(GOLD_DIR, 'header.txt')
    LTE__CUR_MONEY_TEMP = u'低于设定阈值：{:.2f} 元\n当前价格：{:.2f} 元\n'
    GTE__CUR_MONEY_TEMP = u'高于设定阈值：{:.2f} 元\n当前价格：{:.2f} 元\n'

    def __init__(self):
        self.fd_obj = RawToPython(self.FD_FILE_PATH)
        self.cur_money = self.refresh_cur_money()
        self.lte__cur_money_tmp = 0
        self.gte__cur_money_tmp = 0

    def refresh_cur_money(self):
        web_data = self.fd_obj.requests()
        # re_finds = re.findall(r'lineChartData.*?=(.+?);', web_data.text)
        re_finds = re.findall(r'<dd><b>(.+?)</b><i class="up"></i>.*?</dd>',
                              web_data.text)
        self.cur_money = float(re_finds[0])
        return self.cur_money

    def lte__cur_money(self, value):
        value = float(value)
        if self.cur_money <= value and self.lte__cur_money_tmp != value:
            self.lte__cur_money_tmp = value
            return self.LTE__CUR_MONEY_TEMP.format(value, self.cur_money)
        return ''

    def gte__cur_money(self, value):
        value = float(value)
        if self.cur_money >= value and self.gte__cur_money_tmp != value:
            self.gte__cur_money_tmp = value
            return self.GTE__CUR_MONEY_TEMP.format(value, self.cur_money)
        return ''

    def clear(self):
        self.lte__cur_money_tmp = 0
        self.gte__cur_money_tmp = 0

CUR_MONEY_TEMP = u'当前价格：{:.2f} 元\n'

GOLD_LINK = u'\nhttp://t.cn/R9BAmdm'


if __name__ == '__main__':
    itchat_obj = WechatObject()
    # itchat_obj.test()
    make_obj = GoldMake()
    set_obj = WechatSet()
    itchat_obj.send_msg(CUR_MONEY_TEMP.format(make_obj.cur_money))
    # print web_data.text
    next_time = 0
    clear_time = 0
    itchat_obj.run(False)
    msg = ''
    while True:
        now_time = int(time.time())
        if next_time < now_time:
            json_data = set_obj.get_json()
            make_obj.refresh_cur_money()
            msg = make_obj.lte__cur_money(json_data['set_down_func'])
            msg += make_obj.gte__cur_money(json_data['set_upper_func'])
            if msg:
                itchat_obj.send_msg(msg)
            next_time = now_time + random.randint(10, 20)
        if clear_time < now_time:
            clear_time = now_time + 600
            make_obj.clear()
        time.sleep(1)
