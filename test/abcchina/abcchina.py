#!/usr/bin/python
# - * - encoding: UTF-8 - * -
from utils.fiddler import RawToPython

token_raw = RawToPython('txt/get_token.txt')
token_data = token_raw.requests()
token = token_data.json()['result']['token']

send_token_raw = RawToPython('txt/send_token.txt')
send_token_raw.set_param(req_param={'token': token})
token_data = send_token_raw.requests()

chou_raw = RawToPython('txt/chou.txt')
chou_raw = chou_raw.requests()
print chou_raw.json()
