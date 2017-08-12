#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import json

import os

from gold_reminder.settings import GOLD_DIR





class MsgTest(object):
    def __init__(self, text):
        self.text = text


o = WechatReply(MsgTest(u'#下#123'))
print o.analysis_cmd()
