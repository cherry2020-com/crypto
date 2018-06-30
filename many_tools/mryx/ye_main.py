#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import time
import pickle

from utils.fiddler import RawToPython

COUNT = 1

# head_file = './ye_head_for_me.txt'
head_file = 'ye_head_for_girl.txt'
code_file = 'ye_codes.txt'

# code
raw = RawToPython('./txt/' + head_file)
count = 0
with open('./txt/' + 'used.txt') as f:
    used_codes = pickle.load(f)

with open('./txt/' + code_file) as cs:
    for line in cs:
        code = line.strip()
        if not code:
            continue
        if code in used_codes:
            continue
        raw.set_param(url_param={'inviteCode': code})
        wb_data = raw.requests()
        msg = wb_data.json()['msg']
        print code, msg
        used_codes.add(code)
        if msg == u'兑换余额成功':
            count += 1
        if count == COUNT:
            break
        time.sleep(random.randint(1, 5))

with open('./txt/' + 'used.txt', 'wb+') as f:
    pickle.dump(used_codes, f)
print "END !!!"
