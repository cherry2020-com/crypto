#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import time

import sys

from utils.buying_times import PanicBuyingTimes
from utils.fiddler import RawToPython, FiddlerRequestException

file_path = sys.argv[1]
req = RawToPython(file_path)
buying_time = PanicBuyingTimes("20:00:00")
while True:
    if buying_time.start(debug=True):
        try:
            web_data = req.requests(timeout=(None, 0.01))
            # web_data = req.requests(timeout=(None, None))
            print web_data.json()['subCodeMsg']
        except FiddlerRequestException:
            pass
    else:
        time.sleep(0.2)
