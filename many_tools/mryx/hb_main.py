#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import time
import pickle
import sys
import urllib3

from utils.fiddler import RawToPython
urllib3.disable_warnings()
sys.path.extend(['/data/my_tools_env/my_tools/'])
COUNT = 10

head_file = 'hb_head_for_me.txt'
# head_file = 'hb_head_for_girl.txt'
code_file = 'hb_codes.txt'

# code
raw = RawToPython('./txt/' + head_file)
count = 0
with open('./txt/' + 'used.txt') as f:
    used_codes = pickle.load(f)

with open('./txt/' + code_file) as cs:
    for index, line in enumerate(cs):
        if count == COUNT:
            break
        code = line.strip()
        if not code:
            continue
        if code in used_codes:
            continue
        raw.set_param(req_param={'discount_code': code})
        wb_data = raw.requests()
        msg = wb_data.json()['msg']
        print u'红包', index, code, msg
        used_codes.add(code)
        if msg != u'兑换码无效':
            count += 1
        time.sleep(random.randint(1, 5))

with open('./txt/' + 'used.txt', 'wb+') as f:
    pickle.dump(used_codes, f)
print "END !!!"
