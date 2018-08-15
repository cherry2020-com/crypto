#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils.buying_times import PanicBuyingTimes
from utils.fiddler import RawToPython, FiddlerRequestException

req = RawToPython('./head.txt')
buying_time = PanicBuyingTimes("2018-08-15 10:00:00")
while True:
    try:
        if buying_time.is_start:
            web_data = req.requests(timeout=(None, 0.01))
            # web_data = req.requests(timeout=(None, None))
            print web_data.json()['subCodeMsg']
    except FiddlerRequestException:
        pass
