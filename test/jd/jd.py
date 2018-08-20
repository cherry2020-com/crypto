#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import time

import sys

from utils.buying_times import PanicBuyingTimes
from utils.fiddler import RawToPython, FiddlerRequestException

file_path = sys.argv[1]
req = RawToPython(file_path)
buying_time = PanicBuyingTimes("2018-08-20 00:00:00")
count = 0
heart_count = 1
while True:
    if buying_time.start(debug=True, other_info='{}/{}'.format(count + 1, heart_count)):
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
