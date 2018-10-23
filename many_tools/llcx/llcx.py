#!/usr/bin/env python
# coding=utf-8

import datetime
import os
import sys

sys.path.extend(['/data/my_tools_env/my_tools/'])
from utils.fiddler import RawToPython

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def query():
    def _get_data(web_data, stat_month, start_with):
        web_data.set_param(url_param={'statMonth': stat_month})
        web_json = web_data.requests(timeout=10).json()
        results = web_json['result']
        all_used = 0
        count = 0
        for each in results:
            if not each['sessionTime'].startswith(start_with):
                break
            all_used += each['usage']
            count += 1
        return all_used, count

    web_data = RawToPython(os.path.join(CUR_DIR, 'head', 'liuliang.txt'))
    now = datetime.datetime.now()
    stat_month = now.strftime('%Y%m')
    start_with = now.strftime('%Y-%m-%d')
    all_used, count = _get_data(web_data, stat_month, start_with)
    if not all_used:
        next_month = now.month + 1
        next_year = now.year
        if next_month == 13:
            next_month = 1
        next_stat_month = "{}{:0>2}".format(next_year, next_month)
        all_used, count = _get_data(web_data, next_stat_month, start_with)
    used_g = float(all_used) / 1024 / 1024
    web_json = {'date': start_with, 'used': "{:.4f} G".format(used_g),
                'times': "{} times".format(count)}
    return web_json


print(query())
