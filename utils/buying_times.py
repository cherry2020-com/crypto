#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import Queue
import datetime
import random
import time


class PanicBuyingTimesException(Exception):
    pass


class PanicBuyingTimes(object):
    def __init__(self, date_times, before_seconds=3, after_seconds=5,
                 false_sleep_second_randint_param=None, true_sleep_second=None,
                 debug_info=True):
        self.before_seconds = before_seconds
        self.after_seconds = after_seconds
        self.debug_info = debug_info
        self.false_sleep_second_randint_param = false_sleep_second_randint_param or (0, 0)
        self.true_sleep_second = true_sleep_second
        self.date_times_queue = Queue.Queue()
        if isinstance(date_times, str):
            date_times = [date_times]
        date_times = self._make_correct_date_times(date_times)
        date_times = self.make_date_times(date_times)
        self._remove_expired_times(date_times)
        try:
            self.this_time = self.date_times_queue.get(block=False)
        except Queue.Empty:
            raise PanicBuyingTimesException('Error: Had not times to wait !')

    @staticmethod
    def _make_correct_date_times(date_times):
        new_date_times = []
        for date_time in date_times:
            date_time = date_time.strip()
            if len(date_time) == len('00:00:00'):
                date_time = "{} {}".format(
                    datetime.date.today().strftime('%Y-%m-%d'),
                    date_time)
            new_date_times.append(date_time)
        return new_date_times

    @staticmethod
    def make_date_times(date_times):
        new_date_times = []
        for date_time in date_times:
            new_date_times.append(datetime.datetime.strptime(
                date_time, "%Y-%m-%d %H:%M:%S"))
        return new_date_times

    def _remove_expired_times(self, date_times):
        now = datetime.datetime.now()
        new_date_times = []
        for date_time in date_times:
            start_date_time = date_time - datetime.timedelta(
                seconds=self.before_seconds)
            if date_time > now:
                end_date_time = date_time + datetime.timedelta(
                    seconds=self.after_seconds)
                new_date_times.append([start_date_time, end_date_time])
        date_times = sorted(new_date_times, key=lambda x: x[0])
        for date_time in date_times:
            self.date_times_queue.put(date_time)

    @property
    def is_start(self):
        _is_start = self._start()
        if _is_start:
            if self.true_sleep_second:
                if self.debug_info:
                    print "IS_START: True | Sleep Time: {}s".format(self.true_sleep_second)
                time.sleep(self.true_sleep_second)
        else:
            sleep_time = random.randint(*self.false_sleep_second_randint_param)
            if self.debug_info:
                print "IS_START: False | Sleep Time: {}s".format(sleep_time)
            for _ in xrange(sleep_time * 10):
                time.sleep(0.1)
                _is_start = self._start(debug_info=False)
                if _is_start:
                    return True

    def _start(self, debug_info=None):
        debug_info = debug_info if debug_info is not None else self.debug_info
        now = datetime.datetime.now()
        start_time, end_time = self.this_time
        if start_time <= now <= end_time:
            if debug_info:
                print "IS_START: True | [{}] == [{}]".format(
                    start_time, now.strftime("%Y-%m-%d %H:%M:%S"))
            return True
        if now >= end_time:
            try:
                self.this_time = self.date_times_queue.get(block=False)
            except Queue.Empty:
                raise PanicBuyingTimesException('Error: Had not times to wait !')
        if debug_info:
            print "IS_START: False | [{}] == [{}]".format(
                start_time, now.strftime("%Y-%m-%d %H:%M:%S"))
        return False


if __name__ == '__main__':
    a = PanicBuyingTimes(['22:47:00', '2018-07-15 09:52:00',
                          '22:55:00', '2018-08-15 22:28:00'],
                         false_sleep_second_randint_param=(60, 70), true_sleep_second=0.01)
    while True:
        now = datetime.datetime.now()
        if a.is_start:
            print "T - {}".format(now)
        else:
            print "F - {}".format(now)
        # time.sleep(1)
