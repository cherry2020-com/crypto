#!/usr/bin/python
# -*- coding: UTF-8 -*-
APP_ACCESS_TOKEN = 'MCqhTzJ58RwhvS-1N7BWzAE_ifWGJhWEQcbVMmCCEPg'  # 执行前需要替换！！！

IS_DEBUG_SUBMIT = False  # DEBUG使用，正式使用时请关闭False
IS_DEBUG_TIME = False  # DEBUG使用，正式使用时请关闭False
FILE_PATH = './fuchan_head'  # 程序使用，指定替换APP_ACCESS_TOKEN后文件存储位置

SLOW_TIMEOUT = 8  # 脚本除了在执行提交预约时，请求的超时时间。时间尽量保持在5-10秒。
FAST_TIMEOUT = 2  # 脚本在执行提交预约时，请求的超时时间。时间越短抢到概率越大，但时间过短看不到是否预约成功
HARD_TIMEOUT = 0.1  # 02_hard_book.py 脚本使用时间，不推荐使用该脚本
ERROR_COUNT = 10  # 脚本在执行提交预约时，如果错误几次脚本将退出提交，重新扫描医生可选时间

RUSH_TIME = '15:30:00'  # 放号时间
RUSH_TIME_MINUTES_EARLY = 2  # 脚本快扫描的提前量(单位：分钟)
RUSH_TIME_MINUTES_LAG = 3  # 脚本快扫描的滞后量(单位：分钟)
TIME_RANDOM_RANGE = [5, 12]  # 脚本慢扫描时间范围（单位：秒）
FAST_TIME_RANDOM_RANGE = [3, 5]  # 脚本快扫描时间范围（单位：秒）
# FAST_TIME_RANDOM_RANGE = [1, 1]


HAS_CARD = True  # 是否有妇产医院的卡
HOSPITAL = u'总院'  # 医院名称
DEPARTMENT = u'产一门诊'  # 门诊名称
DOCTOR = u'李颖'  # 医生名称
DATE = u'2021-10-08'  # 预约日期
TIME = u'08:00'  # 期望预约的大致时间。不需要准确的医生时间，脚本会自动寻找接近的时间预约。
# HOSPITAL = u'总院'
# DEPARTMENT = u'产科门诊'
# DOCTOR = u'战芳'
# DATE = u'2021-09-15'
# TIME = u'08:15'


