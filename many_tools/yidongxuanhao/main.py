#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

from utils.fiddler_session import RawToPython

raw = RawToPython('./head.txt')
all_numbers = set()
with open('./xuanhao.txt') as f:
    f_all = f.read()
all_numbers = set(f_all.strip().split('\n'))
i = 0
try:
    while i <= 3000:
        web_data = raw.requests()
        web_json = web_data.json()
        this_numbers = []
        for each in web_json['data']:
            this_numbers.append(each['number'])
        new_numbers = set(this_numbers) - all_numbers
        print 'new: {}, total: {}, count:{}'.format(len(new_numbers), len(all_numbers), i)

        if new_numbers:
            print ', '.join(list(new_numbers))
            all_numbers.update(new_numbers)
            # break
        i += 1
except Exception:
    pass

with open('./xuanhao.txt', 'wb+') as f:
    for x in all_numbers:
        f.write(str(x) + '\n')