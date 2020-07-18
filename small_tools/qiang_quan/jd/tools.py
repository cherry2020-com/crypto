#!/usr/bin/python
# -*- coding: UTF-8 -*-
import datetime
import time

from utils.fiddler_session import RawToPython


def get_jd_time(_type='datetime'):
    """

    :param _type: datetime/timestamp
    :return:
    """
    rtp = RawToPython('./head/get_jd_time.txt')
    web = rtp.requests(timeout=5)
    server_time = web.json()['serverTime']

    if _type == 'datetime':
        return datetime.datetime.fromtimestamp(float(server_time)/1000)
    if _type == 'timestamp':
        return int(server_time)
    raise Exception('get_jd_time: unknown _type???')


def get_time_diff():
    datetime.datetime.now()
    jd_timestamp = get_jd_time('timestamp')
    return jd_timestamp - int(time.time() * 1000)


if __name__ == '__main__':
    # print get_jd_time()
    # print get_time_diff()
    # a = get_jd_time()
    a = time.time()
    b = datetime.datetime.fromtimestamp(a)
    c = datetime.datetime.fromtimestamp(a+1) - datetime.timedelta(seconds=1, milliseconds=1)
    print a, b, c
