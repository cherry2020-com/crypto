#!/usr/bin/python
# - * - encoding: UTF-8 - * -

import datetime
import random
import json
import time
import sys
import os
sys.path.extend(['/data/my_tools_env/my_tools/'])


from utils.fiddler import RawToPython, FiddlerRequestTimeOutException, \
    FiddlerRequestException
from utils.send_email import Email
from utils import tools
import urllib3

urllib3.disable_warnings()
GOLD_DIR = os.path.dirname(os.path.abspath(__file__))
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
        my_source = 's-3c91ca69-dd35-4275-9d59-5a0608fd'
        receiver_source = 'g-d22d57b4-1dda-4888-84b9-57a92766'
        url = 'http://t.cn/RVCjPNI'
        content = msg
        title = u'Gold Reminder'
        tools.send_push(content, url, my_source, receiver_source, title)


class GoldMake(object):
    FD_FILE_PATH = os.path.join(GOLD_DIR, 'head', 'icbc.txt')
    LTE__CUR_MONEY_TEMP = u'低于阈值：¥{:.2f} | '
    GTE__CUR_MONEY_TEMP = u'高于阈值：¥{:.2f} | '
    SEP__UP_CUR_MONEY_TEMP = u'上涨：¥{:.2f} | '
    SEP__DOWN_CUR_MONEY_TEMP = u'下跌：¥{:.2f} | '
    NEW_HIGH_MONEY_TEMP = u'新【高】：¥{:.2f} | '
    NEW_LOW_MONEY_TEMP = u'新【低】：¥{:.2f} | '

    MONEY_TEMP = u'涨跌：¥{up_down}\n' \
                 u'当前：↑¥{buy_cur:.2f} (¥{jst_cur:.2f} ${dollar_cur:.2f}) | ↓¥{sell_cur:.2f}\n' \
                 u'最高：¥{high:.2f} | 最低：¥{low:.2f}'

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

    def _get_web_data(self):
        web_data = self.fd_obj.requests()
        web_json = web_data.json()
        market = web_json['market']
        return {x['metalname']: x for x in market}

    def refresh_cur_money(self):
        try:
            web_data = self._get_web_data()
            gold_data = web_data[u'人民币账户黄金']
            dollar_gold_data = web_data[u'美元账户黄金']
            self.cur_money = float(gold_data['middleprice']) + 0.2
            self.jst_cur_money = self.cur_money - 0.4 + 3.58
            self.sell_cur_money = self.cur_money - 0.4
            self.high_money = float(gold_data['topmiddleprice']) + 0.2
            self.low_money = float(gold_data['lowmiddleprice']) + 0.2
            self.float_money = gold_data['openprice_dv']

            self.dollar_cur_money = float(dollar_gold_data['middleprice']) + 0.9
            self.dollar_high_money = float(dollar_gold_data['topmiddleprice']) + 0.9
            self.dollar_low_money = float(dollar_gold_data['lowmiddleprice']) + 0.9
            self.dollar_float_money = dollar_gold_data['openprice_dv']
        except FiddlerRequestTimeOutException as e:
            time.sleep(60)
            self.cur_money = self.refresh_cur_money()
        except Exception as e:
            tools.send_error_msg_by_email("[icbc]refresh_cur_money: " + str(e))
            time.sleep(60)
            self.cur_money = self.refresh_cur_money()
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
            difference = self.cur_money - self.start_money
            sep_money = abs(difference) - value
            if sep_money >= 0:
                self.start_money = self.cur_money
                if difference > 0:
                    msg = self.SEP__UP_CUR_MONEY_TEMP.format(value, self.cur_money)
                else:
                    msg = self.SEP__DOWN_CUR_MONEY_TEMP.format(value, self.cur_money)
                return msg
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
            buy_cur=self.cur_money, dollar_cur=self.dollar_cur_money,
            high=self.high_money, dollar_high=self.dollar_high_money,
            low=self.low_money, dollar_low=self.dollar_low_money,
            up_down=self.float_money, dollar_update=self.dollar_float_money,
            jst_cur=self.jst_cur_money, sell_cur=self.sell_cur_money)

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
    json_data = set_obj.get_json()
    while True:
        now_time = int(time.time())
        if next_time < now_time:
            print 'refresh|'
            make_obj.refresh_cur_money()
            msg = make_obj.get_msg(json_data.get('set_upper_func'),
                                   json_data.get('set_down_func'),
                                   json_data.get('set_float_func'),
                                   json_data.get('set_high_low_float_func'))
            if msg:
                print '%s: send msg|' % datetime.datetime.now()
                itchat_obj.send_msg(msg)
            next_time = now_time + random.randint(5, 8)
            sys.stdout.flush()
        if clear_time < now_time:
            clear_time = now_time + 600
            make_obj.clear()
        time.sleep(1)
        print 'step|',


if __name__ == '__main__':
    do_while()
