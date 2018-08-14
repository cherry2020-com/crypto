#!/usr/bin/python
# - * - encoding: UTF-8 - * -

import time

import sys
import urllib3
sys.path.extend(['/data/my_tools_env/my_tools/'])

from utils import tools

urllib3.disable_warnings()

HIGH_TEMP = 68
TIME_SEP = 10


if __name__ == '__main__':
    last_time = time.time()
    my_source = 's-fe1932f8-0799-42e6-b271-20b59ce4'
    receiver_source = 'g-7d2bb46f-3163-4e86-9960-0de6973d'
    title = u'System Reminder'
    while True:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = float(f.read()) / 1000
        print u'{:.2f}'.format(temp)
        # temp = 66
        if temp >= HIGH_TEMP:
            now_time = time.time()
            if now_time - last_time > TIME_SEP:
                last_time = now_time
                tools.send_push(u'[SYS]树莓派温度过高: {:.2f}'.format(temp), None,
                                my_source, receiver_source, title)

        time.sleep(30)
