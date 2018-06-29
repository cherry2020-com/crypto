#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import time

from utils.fiddler import RawToPython

raw = RawToPython('head.txt')
codes = set()
with open('phone_codes.txt') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        codes.add(line)
code_len = len(codes)
code_count = 0
count = 0
hasRegisters = [u"HasLogged", u"HasRegistered"]
hasAwards = [u"HasReward", u"NoReward"]
with open('phones.txt', 'wb+') as f:
    for code in codes:
        number = 0
        code_count += 1
        while True:
            number += 1
            raw.set_param(url_param={'page': number, 'phone': code})
            web_data = raw.requests()
            rows = web_data.json()['rows']
            if not rows:
                break
            for row in rows:
                count += 1
                f.write("{phone} {login} {award}\n".format(
                    phone=row['phone'],
                    login=hasRegisters[row['hasRegister']],
                    award=hasAwards[row['hasRegister']])
                )
                print 'Count:', count, 'Code:', code, 'Page:', number, 'Phone:', row['phone'], '%:', "%s/%s" % (code_count, code_len)
            if len(rows) < 7:
                break
            time.sleep(0.3)
