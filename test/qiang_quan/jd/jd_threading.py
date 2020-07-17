#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import random
import threading
import time

import sys
import uuid

from utils.buying_times import PanicBuyingTimes, PanicBuyingTimesException
from utils.fiddler import RawToPython, FiddlerRequestException


def request_jd(req_jd):
    try:
        print '-->:', threading.current_thread().name
        web_data = req_jd.requests(timeout=2)
        print web_data.json()['subCodeMsg']
    except FiddlerRequestException:
        pass


if __name__ == '__main__':
    file_path = sys.argv[1]
    date_times = "2020-07-17 00:00:00"
    date_times = sys.argv[2] if len(sys.argv) == 3 else date_times
    buying_time = PanicBuyingTimes(date_times, false_sleep_second_randint=(30, 60),
                                   debug=True)
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
                time.sleep(0.3)
            else:
                try:
                    web_data = req.requests(timeout=5)
                    print web_data.json()['subCodeMsg']
                except FiddlerRequestException:
                    pass
        except PanicBuyingTimesException as e:
            print e
            break
        except Exception as e:
            print e
        finally:
            for t in threadings:
                t.join(timeout=2)
