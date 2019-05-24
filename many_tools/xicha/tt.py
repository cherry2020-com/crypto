#!/usr/bin/python
# -*- coding: UTF-8 -*-
j = {'name': u'三里屯'}
tip_temp = u"""osascript -e 'display notification "{content}" with title "{title}"'""".format(
                content=u'快快快，可以买【{}】的喜茶啦！'.format(j['name']), title=u'喜茶')
import os
os.system(tip_temp.encode('utf-8'))
