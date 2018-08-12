#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import time

from utils.fiddler import RawToPython

raw = RawToPython('head.txt')
codes = set()
with open('1.phone_codes.txt') as f:
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

file_num = 1
file_lines = []
for code in codes:
    number = 0
    code_count += 1
    while True:
        number += 1
        raw.set_param(url_param={'page': number, 'phone': code})
        try:
            web_data = raw.requests(timeout=10)
            rows = web_data.json()['rows']
        except Exception:
            break
        if not rows:
            break
        for row in rows:
            count += 1
            file_lines.append("{phone} {login} {award}\n".format(
                phone=row['phone'],
                login=hasRegisters[row['hasRegister']],
                award=hasAwards[row['hasRegister']])
            )
            print 'Count:', count, 'Code:', code, 'Page:', number, 'Phone:', row['phone'], '%:', "%s/%s" % (code_count, code_len)
            if count / 10000 == file_num:
                with open('./phones/phones_part_{}.txt'.format(file_num), 'wb+') as f:
                    f.writelines(file_lines)
                file_lines = []
                file_num += 1

        if len(rows) < 7:
            break
        time.sleep(0.2)
