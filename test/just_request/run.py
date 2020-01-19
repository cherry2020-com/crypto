#!/usr/bin/python
# -*- coding: UTF-8 -*-
import time

from utils.fiddler import RawToPython
f = RawToPython('./head.txt')
a = None
while True:
    web_json = f.requests().json()
    if a is None:
        a = web_json
    if a != web_json:
        break
    print(web_json)
    time.sleep(5)