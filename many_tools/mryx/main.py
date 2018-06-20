#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import time

from utils.fiddler import RawToPython

raw = RawToPython('./ye_head_for_me.txt')
count = 0
with open('codes.txt') as cs:
    for line in cs:
        count += 1
        if count == 11:
            break
        code = line.strip()
        if not code:
            continue
        raw.set_param(url_param={'inviteCode': code})
        wb_data = raw.requests()
        time.sleep(random.randint(1, 5))
        print code, wb_data.json()['msg']
