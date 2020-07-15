#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import sys

sys.path.extend(['/data/my_tools_env/my_tools/'])
import itchat
import urllib3
from utils import pusher

urllib3.disable_warnings()


# isFriendChat=True
# isGroupChat=True
# isMpChat=True
KEY_MESSAGES = [u'放水', u'秒到', u'速度', u'抓紧', u'提现', u'发低保',
                u'领低保', u'到了', u'水了']
MSG_TEMP = u"{content}\nFrom: [{group}]-[{who}]"


@itchat.msg_register(itchat.content.TEXT, isFriendChat=True, isGroupChat=True)
def text_reply(msg):
    try:
        # if msg['User']['NickName'].startswith(u'黄金'):
        if_content = msg['Content'].replace(' ', '')
        for k in KEY_MESSAGES:
            if k in if_content:
                user = msg.get('User', {})
                send_msg = MSG_TEMP.format(
                    content=msg['Content'],
                    group=user.get('NickName', ''),
                    who=msg.get('ActualNickName', ''))
                my_source = 's-deb121a7-44f5-4674-a889-ed08c358'
                receiver_source = 'g-d7c27573-6be5-4c03-b6a4-e116256c'
                # url = 'com.icbc.iphoneclient://'
                url = 'https://www.wanjiajinfu.com/'
                content = send_msg
                title = u'华夏万家'
                sound = 'failling'
                pusher.send(my_source, receiver_source, title=title, url=url,
                            content=content, sound=sound)
                break
    except Exception:
        pass


class WechatObject(object):

    def __init__(self, enable_cmd_qr=False):
        itchat.auto_login(enableCmdQR=enable_cmd_qr, hotReload=True)

    def run(self, block_thread=False):
        itchat.run(blockThread=block_thread)


if __name__ == '__main__':
    itchat_obj = WechatObject(enable_cmd_qr=False)
    itchat_obj.run(block_thread=True)
