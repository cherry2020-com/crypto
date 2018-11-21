#!/usr/bin/python
# -*- coding: UTF-8 -*-

from pushbullet import Pushbullet

api_key = 'o.4UaP0xplMx9vrNmteb7n4Uw0b7IByDel'
pb = Pushbullet(api_key)
print(pb.channels)
my_channel = pb.get_channel('zk8')
push = pb.push_note("This is the title zk8", "This is the body", channel=my_channel)
# print push
# push = pb.push_link("Cool site", "https://github.com")
# print push
