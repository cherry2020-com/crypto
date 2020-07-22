#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import sys
from datetime import datetime

from small_tools.qiang_quan.jd.tools import get_time_diff
from utils.buying_times import PanicBuyingTimes, PanicBuyingTimesException
from utils.fiddler import RawToPython, FiddlerRequestException

imp_templ = u'\033[1;33;44m{}\033[0m'

if __name__ == '__main__':
    file_path = sys.argv[1]
    date_times = "2020-07-22 14:17:00"
    time_diff_ms = get_time_diff()
    print '-->time_diff_ms', time_diff_ms
    date_times = sys.argv[2] if len(sys.argv) == 3 else date_times
    buying_time = PanicBuyingTimes(date_times, before_seconds=1,
                                   after_seconds=0,
                                   false_sleep_second_randint=(60, 120),
                                   debug=True, time_diff_ms=time_diff_ms)
    req = RawToPython(file_path)
    count = 0
    heart_count = 1
    while True:
        try:
            if buying_time.is_start:
                print '--> START !!!', datetime.now()
                web_data = req.requests(timeout=(0.5, 0.001))
                print imp_templ.format(web_data.json()['subCodeMsg'])
            else:
                try:
                    web_data = req.requests(timeout=5)
                    print imp_templ.format(web_data.json()['subCodeMsg'])
                except FiddlerRequestException:
                    pass
        except PanicBuyingTimesException as e:
            print '-->ERROR:PanicBuyingTimesException:', e
            break
        except Exception as e:
            print '-->ERROR:Exception:', e
