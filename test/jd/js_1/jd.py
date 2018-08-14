#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils.fiddler import RawToPython, FiddlerRequestException

req = RawToPython('./head.txt')
while True:
    try:
        web_data = req.requests(timeout=(None, 0.01))
        # web_data = req.requests(timeout=(None, None))
        print web_data.json()['subCodeMsg']
    except FiddlerRequestException:
        pass
