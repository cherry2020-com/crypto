#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

from utils.fiddler import RawToPython

rtp = RawToPython('./tt.head')
count = 0
while True:
    count += 1
    web = rtp.requests(timeout=5)
    print count, web.status_code, web.json()[0]['message']
    # time.sleep(0.1)
