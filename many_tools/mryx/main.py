#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils.fiddler import RawToPython

raw = RawToPython('./ye_head.txt')
with open('codes.txt') as cs:
    for line in cs:
        code = line.strip()
        if not code:
            continue
        raw.set_param(url_param={'inviteCode': code})
        wb_data = raw.requests()
        print wb_data.json()['msg']
