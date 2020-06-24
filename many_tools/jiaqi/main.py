#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pprint

import datetime
from bs4 import BeautifulSoup


line_year = 2018

with open('./Employee Time Off_ Home _ Salesforce - Unlimited Edition.html') as f:
    web_data = f.read()
soups = BeautifulSoup(web_data, "lxml")
_all_items = soups.findAll(class_='dataRow')
_all_titles = soups.findAll(class_='zen-deemphasize')
all_titles = [x.text for x in _all_titles]
all_items = []

for each in _all_items:
    all_items.append(dict(zip(all_titles, [x.text for x in each])))

all_templ = ''
valid_items = []
for _index, _item in enumerate(all_items):
    all_templ += u'{: >3}: '.format(_index)
    _each_templs = []
    for _title in all_titles:
        _each_templs.append(u'{}: {}'.format(_title, _item[_title]))
    all_templ += u'\t'.join(_each_templs) + '\r\n'
    if _item['Type'] == 'Vacation (except for France)':
        valid_items.append(_item)
print u'-->\r\n' + all_templ
print u'--> 共请假{}次，其中年假{}次'.format(len(all_items), len(valid_items))
print u'--> {0}年以下按10天计算， {0}年（含）以后按15天计算'.format(line_year)
jia_map = {}
for _item in all_items:
    start_date = _item['Start Date']
    year = int(start_date.split('/')[-1])
    jia_map.setdefault(year, 0.0)
    jia_map[year] += float(_item['Calculated Days Off'])
print u'--> 统计(整年):', jia_map


start_year = min(jia_map.keys())
end_year = max(jia_map.keys())
all_jia_map = {}
for _year in range(start_year, end_year + 1):
    all_jia_map[_year] = float(10 if _year < line_year else 15)

all_items.reverse()
for _index, _item in enumerate(all_items):
    if _item['Type'] != 'Vacation (except for France)':
        print u'{}: 其他类型假期，不参与年假计算({})'.format(_index, _item['Type'])
        continue
    start_date = _item['Start Date']
    month, _, year = [int(x) for x in start_date.split('/')]
    _used = float(_item['Calculated Days Off'])
    new_year = year
    if 1 <= month <= 6:
        new_year -= 1
        if new_year not in all_jia_map:
            new_year = year
    all_jia_map[new_year] -= _used
    if all_jia_map[new_year] < 0:
        next_days = all_jia_map[new_year]
        all_jia_map[new_year] = 0
        print u'{}: {}年{}月请假{}天，使用{}年{}天年假，该年度剩余{}天年假 |>'.format(
            _index, year, month, _used, new_year, _used + next_days, all_jia_map[new_year])
        new_year += 1
        all_jia_map[new_year] += next_days
        print u'{}: {}年{}月请假{}天，使用{}年{}天年假，该年度剩余{}天年假 |<'.format(
            _index, year, month, _used, new_year, -next_days, all_jia_map[new_year])

        assert all_jia_map[new_year] >= 0
    else:
        print u'{}: {}年{}月请假{}天，使用{}年{}天年假，该年度剩余{}天年假'.format(
            _index, year, month, _used, new_year, _used, all_jia_map[new_year])

pp = pprint.PrettyPrinter(indent=1)
pp.pprint(all_jia_map)
today = datetime.date.today()
if today.month <= 6:
    print u'-->截止{}年6月，你还有{}天的年假'.format(
        today.year, all_jia_map[today.year-1])
print u'-->截止{}年6月，你还有{}天的年假'.format(
        today.year + 1, all_jia_map[today.year])
