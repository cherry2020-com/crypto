#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils import pusher

my_source = 's-3c91ca69-dd35-4275-9d59-5a0608fd'
receiver_source = 'g-d22d57b4-1dda-4888-84b9-57a92766'
url = 'com.icbc.iphoneclient://'
content = "Hello world",
title = u'黄金提醒'
pusher.send(my_source, receiver_source, title=title, url=url, content=content)
