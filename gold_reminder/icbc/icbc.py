#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils.fiddler import RawToPython
from utils.send_email import Email


class ICBC(object):
    FLOAT_MONEY_TEMP = u'涨浮：{:.2f} 元 | '
    MONEY_TEMP = u'当前：{:.2f} 元\n'

    def __init__(self):
        self.fd = RawToPython('raw.txt')
        self.web_json = None

        self.cur_money = None
        self.start_money = None

    def refresh(self):
        web_data = self.fd.requests()
        try:
            self.web_json = web_data.json()
        except Exception:
            self.web_json = None

    def resolve(self):
        """
        人民币账户黄金/人民币账户白银/人民币账户铂金/人民币账户钯金/
        美元账户黄金/  美元账户白银/  美元账户铂金/ 美元账户钯金
        """
        if not self.web_json:
            return
        market_map = {}
        for market in self.web_json['market']:
            market_map[market['metalname']] = market['buyprice']
        return market_map


class MakeGold(object):
    FLOAT_MONEY_TEMP = u'涨浮：{:.2f} 元 | '
    MONEY_TEMP = u'当前：{:.2f} 元\n'

    def __init__(self, cur_money):
        self.cur_money = cur_money
        self.start_money = cur_money

    def float_money(self, value):
        if value and self.start_money and self.cur_money:
            value = float(value)
            sep_money = abs(self.start_money - self.cur_money) - value
            if sep_money >= 0:
                self.start_money = self.cur_money
                return self.FLOAT_MONEY_TEMP.format(value, self.cur_money)
        return ''

    def get_msg(self, cur_money):
        msg = self.float_money(cur_money)
        if msg:
            msg += self.MONEY_TEMP.format(cur_money)
        return msg


class SendEmail(object):

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


icbc = ICBC()
icbc.refresh()
print icbc.resolve()
