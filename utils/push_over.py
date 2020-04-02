#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import time
from func_timeout import func_timeout, FunctionTimedOut, func_set_timeout

from pushover import Client, init

# doc: https://pushover.net/api


ALL_TOKENS_MAP = {
    "zk8_new": 'ad7tmvzzxum4hmuauomjtqrg93mryx',
    "zk8_new2": 'a5ddc4pwuk5w9fsxbqfzft2ibmk6ed',
    "zk8_mhot4": 'aqyp1m72x1uen9z69uebzcpotng9rj',
    "zk8_hot": 'afkqikbmthu98ne67rpj394o3a1xr1',
    "zk8_hot2": 'awtyw265rkcp7prdr5dkz8c61mjsfg',
    "zk8_hot3": 'auuxhbsw5fz8wgrt2izexwwvp7cncb',
    "zk8_mhot": 'awzxns7rq6hqrijvbea8sbpk37uzr3',
    "zk8_mhot2": 'a1p2v4duuf4va2unhec8twqbdqdwa2',
    "zk8_mhot3": 'ak2nn7b31xpxh1f5hqrbvvgavtran4',
    "over_7500": 'aabr7ni8r9h9q2dtwj97sy9fty7a1h',
}


class Pushover(object):
    def __init__(self, token_key, sound=False, send_timeout=5):
        user_key = "ugnmvh5cte5hbsecwb1q9fktqt7uw6"
        self.sound = sound
        self.token_key = token_key
        api_token = ALL_TOKENS_MAP[token_key]
        init(api_token, sound)
        self.client = Client(user_key)
        self.date = datetime.date.today()
        self.send_timeout = send_timeout

    def _restart_token(self):
        init(ALL_TOKENS_MAP[self.token_key], self.sound)
        today = datetime.date.today()
        if today > self.date:
            if (self.date.month != today.month and today.day >= 3
                    and self.token_key[-1].isdigit()):
                self.token_key = self.token_key[:-1]
                init(ALL_TOKENS_MAP[self.token_key], self.sound)
            self.date = today

    def _reset_next_token(self):
        if self.token_key == 'over_7500':
            raise Exception('Error for over_7500, Please add new app for pushover!')
        if self.token_key[-1].isdigit():
            _fix = int(self.token_key[-1]) + 1
            self.token_key = self.token_key[:-1] + str(_fix)
        else:
            _fix = 2
            self.token_key = self.token_key + str(_fix)
        if self.token_key not in ALL_TOKENS_MAP:
            self.token_key = 'over_7500'
        init(ALL_TOKENS_MAP[self.token_key], self.sound)

    def send(self, message, **kwargs):
        try:
            result = func_set_timeout(self.send_timeout)(self._send)(message, **kwargs)
        except FunctionTimedOut as e:
            print '--> Send Timeout: {}s: {}'.format(self.send_timeout, str(e))
        else:
            print 'Send_Success |',
            return result

    def _send(self, message, **kwargs):
        """
        message （必填）-您的留言
        可能包括一些可选参数：
        attachment-与邮件一起发送的图像附件；有关如何上传文件的更多信息， 请参见附件
        device -您的用户的设备名称，用于直接将消息发送到该设备，而不是所有用户的设备（多个设备可以用逗号分隔）
        title -您邮件的标题，否则使用您应用的名称
        url- 与您的消息一起显示 的补充URL
        url_title -补充网址的标题，否则仅显示该网址
        priority-发送为-2不生成通知/警报，-1始终以安静的通知发送，1以高优先级显示并绕过用户的安静时间，或者2还需要用户确认
        sound- 设备客户端支持的一种声音名称，以覆盖用户的默认声音选择
        timestamp -您要显示给用户的消息日期和时间的Unix时间戳，而不是我们的API收到消息的时间
        """
        result = None
        self._restart_token()
        try:
            result = self.client.send_message(message, **kwargs)
        except Exception as e:
            e = str(e).strip()
            print ''
            print '--> push_over.py: ', self.token_key
            print '--> push_over.py: ', e
            if "7500" in e:
                self._reset_next_token()
            else:
                time.sleep(1)
            try:
                self.client.send_message(message, **kwargs)
            except Exception as e:
                print '--> Finish: push_over.py: ', e
        return result


if __name__ == '__main__':
    Pushover('zk8_mhot').send('hello word', url='https://pushover.net/api')
