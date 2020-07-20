#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import threading
import time

import sys
import uuid

from small_tools.qiang_quan.jd.tools import get_time_diff
from utils.buying_times import PanicBuyingTimes, PanicBuyingTimesException
from utils.fiddler_session import RawToPython, FiddlerRequestException


IMP_TEMPL = u'\033[1;33;44m{}\033[0m'


def request_jd(req_jd):
    try:
        print '-->:', threading.current_thread().name
        web_data = req_jd.requests(timeout=1)
        print IMP_TEMPL.format(web_data.json()['subCodeMsg'])
    except FiddlerRequestException:
        pass


if __name__ == '__main__':
    file_path = sys.argv[1]
    date_times = "2020-07-20 00:00:00"
    date_times = sys.argv[2] if len(sys.argv) == 3 else date_times
    time_diff_ms = get_time_diff()
    print '-->time_diff_ms', time_diff_ms
    buying_time = PanicBuyingTimes(date_times, before_seconds=0.01,
                                   after_seconds=1,
                                   false_sleep_second_randint=(60, 120),
                                   debug=True, time_diff_ms=time_diff_ms)
    req = RawToPython(file_path)
    count = 0
    heart_count = 1
    threadings = []
    while True:
        try:
            if buying_time.is_start:
                t = threading.Thread(target=request_jd, name=uuid.uuid4(), args=(req, ))
                t.start()
                threadings.append(t)
            else:
                try:
                    web_data = req.requests(timeout=5)
                    print IMP_TEMPL.format(web_data.json()['subCodeMsg'])
                except FiddlerRequestException:
                    pass
        except PanicBuyingTimesException as e:
            print '-->ERROR:PanicBuyingTimesException:', e
            break
        except Exception as e:
            print '-->ERROR:Exception:', e
    for t in threadings:
        t.join(timeout=2)
