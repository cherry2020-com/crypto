# coding: utf-8
# 创建一个session对象
import requests

# s = requests.Session()
# s.get('http://httpbin.org/cookies/set/sessioncookie/123456789')
# r = s.get("http://httpbin.org/cookies")
# print r.text

from utils.fiddler_session import RawToPython
raw = RawToPython('tmp.txt')
r = raw.requests()
print r.text
r = raw.requests('/cookies')
print r.text
