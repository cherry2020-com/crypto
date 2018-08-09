#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils.fiddler import RawToPython

req = RawToPython('head.txt')
web_data = req.requests()
print web_data.json()