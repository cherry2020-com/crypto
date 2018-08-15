#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils.fiddler import RawToPython, FiddlerRequestException
from utils.tools import panic_buying_times

req = RawToPython('./head.txt')
while True:
    try:
        is_start = panic_buying_times("2018-08-15 10:00:00")
        if is_start:
            web_data = req.requests(timeout=(None, 0.01))
            # web_data = req.requests(timeout=(None, None))
            print web_data.json()['subCodeMsg']
    except FiddlerRequestException:
        pass
