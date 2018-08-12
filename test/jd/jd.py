#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils.fiddler import RawToPython

req = RawToPython('./head.txt')
while True:
    try:
        web_data = req.requests(timeout=0.2)
        print web_data.json()['subCodeMsg']
    except Exception:
        pass
