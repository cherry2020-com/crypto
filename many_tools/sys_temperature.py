#!/usr/bin/python
# - * - encoding: UTF-8 - * -

import time

import sys
import urllib3
sys.path.extend(['/data/my_tools_env/my_tools/'])

from utils import pusher

urllib3.disable_warnings()

HIGH_TEMP = 68
TIME_SEP = 10


def send_push(content, url):
    my_source = 's-fe1932f8-0799-42e6-b271-20b59ce4'
    receiver_source = 'g-7d2bb46f-3163-4e86-9960-0de6973d'
    title = u'系统提醒'
    sound = 'default'
    pusher.send(my_source, receiver_source, title=title, url=url,
                content=content, sound=sound)


if __name__ == '__main__':
    last_time = time.time()
    while True:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000
        print u'{:.2f}'.format(temp)
        # temp = 66
        if temp >= HIGH_TEMP:
            now_time = time.time()
            if now_time - last_time > TIME_SEP:
                last_time = now_time
                send_push(u'[SYS]树莓派温度过高: {:.2f}'.format(temp), None)
        time.sleep(30)
