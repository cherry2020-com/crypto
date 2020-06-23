#!/usr/bin/python
# -*- coding: UTF-8 -*-
import pprint

from bs4 import BeautifulSoup


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
print u'--> 2019年以下按10天计算， 2019年（含）以后按15天计算'
jia_map = {}
jia_map_up_6 = {}
jia_map_down_6 = {}
for _item in all_items:
    start_date = _item['Start Date']
    year = int(start_date.split('/')[-1])
    year_6 = year
    jia_map.setdefault(year, 0.0)
    jia_map[year] += float(_item['Calculated Days Off'])
    month = int(start_date.split('/')[1])
    if 1 <= month <= 6:
        jia_map_up_6.setdefault(year, 0.0)
        jia_map_up_6[year] += float(_item['Calculated Days Off'])
    else:
        jia_map_down_6.setdefault(year, 0.0)
        jia_map_down_6[year] += float(_item['Calculated Days Off'])
print u'--> 统计(整年):', jia_map
print u'--> 统计(上半年):', jia_map_up_6
print u'--> 统计(下半年):', jia_map_down_6
line_year = 2019

start_year = min(jia_map.keys())
end_year = max(jia_map.keys())
result = {}
_all_days = 10 if start_year < line_year else 15
_used_days = jia_map.get(start_year, 0) + jia_map_up_6.get(start_year+1, 0)
next_days = 0
if _used_days > _all_days:
    next_days = _used_days - _all_days
    _used_days = _all_days
result[start_year] = {'used': _used_days, 'lave': _all_days-_used_days,
                      'next': next_days}
for _year in range(start_year + 1, end_year + 1):
    _all_days = 10 if _year < line_year else 15
    _used_days = (jia_map_down_6.get(_year, 0) + jia_map_up_6.get(_year+1, 0)
                  + next_days)
    next_days = 0
    if _used_days > _all_days:
        next_days = _used_days - _all_days
        _used_days = _all_days
    result[_year] = {'used': _used_days, 'lave': _all_days - _used_days,
                     'next': next_days}
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(result)
