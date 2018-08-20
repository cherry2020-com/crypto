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
        web_data = req_jd.requests(timeout=1)
        print web_data.json()['subCodeMsg']
    except FiddlerRequestException:
        pass


if __name__ == '__main__':
    file_path = sys.argv[1]
    date_times = sys.argv[2] if len(sys.argv) == 3 else None
    date_times = "2018-08-20 19:10:00"
    buying_time = PanicBuyingTimes(date_times)
    req = RawToPython(file_path)
    count = 0
    heart_count = 1
    threadings = []
    while True:
        try:
            if buying_time.start(debug=True,
                                 other_info='{}/{}'.format(count + 1, heart_count)):
                t = threading.Thread(target=request_jd, name=uuid.uuid4(), args=(req, ))
                t.start()
                time.sleep(0.1)
                threadings.append(t)
            else:
                count += 1
                if count == heart_count:
                    heart_count = random.randint(300, 600)
                    count = 0
                    try:
                        web_data = req.requests(timeout=10)
                        print web_data.json()['subCodeMsg']
                    except FiddlerRequestException:
                        pass
                time.sleep(1)
        except PanicBuyingTimesException as e:
            for t in threadings:
                t.join()
