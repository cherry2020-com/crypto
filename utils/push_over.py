#!/usr/bin/python
# -*- coding: UTF-8 -*-
from pushover import Client, init

# doc: https://pushover.net/api


ALL_TOKENS_MAP = {
    "zk8_new": 'ad7tmvzzxum4hmuauomjtqrg93mryx',
    "zk8_new2": 'a5ddc4pwuk5w9fsxbqfzft2ibmk6ed',
    "zk8_new3": 'aqyp1m72x1uen9z69uebzcpotng9rj',
    "zk8_hot": 'afkqikbmthu98ne67rpj394o3a1xr1',
    "zk8_hot2": 'awtyw265rkcp7prdr5dkz8c61mjsfg',
    "zk8_mhot": 'awzxns7rq6hqrijvbea8sbpk37uzr3',
    "zk8_mhot2": 'a1p2v4duuf4va2unhec8twqbdqdwa2',
    "zk8_mhot3": 'ak2nn7b31xpxh1f5hqrbvvgavtran4',
    "over_7500": 'aabr7ni8r9h9q2dtwj97sy9fty7a1h',
}


class Pushover(object):
    def __init__(self, token_key, sound=False):
        user_key = "ugnmvh5cte5hbsecwb1q9fktqt7uw6"
        self.sound = sound
        self.token_key = token_key
        api_token = ALL_TOKENS_MAP[token_key]
        init(api_token, sound)
        self.client = Client(user_key)

    def _set_token_key(self):
        if self.token_key not in ALL_TOKENS_MAP:
            self.token_key = 'over_7500'

    def send(self, message, **kwargs):
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
        result = self.client.send_message(message, **kwargs)
        if result is None:
            if self.token_key[-1].isdigit():
                _fix = int(self.token_key[-1]) + 1
                self.token_key = self.token_key[:-1] + str(_fix)
            else:
                _fix = 2
                self.token_key = self.token_key + str(_fix)
            self._set_token_key()
            init(self.token_key, self.sound)


if __name__ == '__main__':
    Pushover('over_7500').send('hello word', url='https://pushover.net/api')
