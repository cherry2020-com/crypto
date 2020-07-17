#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random
import sys

import time

from utils.buying_times import PanicBuyingTimes
from utils.fiddler import RawToPython, FiddlerRequestException

file_path = sys.argv[1]
req = RawToPython(file_path)
buying_time = PanicBuyingTimes(["2018-11-27 15:00:00"], debug_info=True)


count = 0
heart_count = 1
while True:
    if buying_time.is_start:
        try:
            web_data = req.requests(timeout=(None, 0.001))
            # web_data = req.requests(timeout=(None, None))
            print web_data.json()['subCodeMsg']
        except FiddlerRequestException:
            pass
    else:
        count += 1
        if count == heart_count:
            heart_count = random.randint(300, 600)
            count = 0
            try:
                web_data = req.requests(timeout=10)
                print web_data.json()['subCodeMsg']
            except FiddlerRequestException:
                pass
        time.sleep(1)
