#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import itchat


@itchat.msg_register(itchat.content.TEXT, isFriendChat=True,
                     isGroupChat=True, isMpChat=True)
def text_reply(msg):
    if msg.get('User') and msg.get('User').get('NickName').startswith(u'黄金'):
        return msg.text
    return u'不支持你！'

if __name__ == '__main__':
    itchat.auto_login(enableCmdQR=False, hotReload=True)
    itchat.send('Hello, filehelper', toUserName='filehelper')
    # all_rooms = itchat.get_chatrooms(update=True, contactOnly=True)
    gold_rooms = itchat.search_chatrooms(name=u'黄金')
    for gold_room in gold_rooms:
        gold_room_name = gold_room['UserName']
        itchat.send('Hello, I am start !', toUserName=gold_room_name)
    itchat.run()


