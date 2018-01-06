#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import json

import re

import requests

phone = 17601605665

with open('html.html') as fr:
    for line in fr:
        line = line.strip()
        data = re.findall(r'"open_url":.*?"(.+?)"', line)
        if data:
            url_part = data[0].replace('\\', '')
            url = 'https:' + url_part + '&phone=' + str(phone) + '&lang=zh-CN'
            request_data = requests.get(url, verify=False)
            print request_data.json()
            print request_data.json().get('errmsg')
