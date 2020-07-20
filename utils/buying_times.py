#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import Queue
import datetime
import random
import time


class PanicBuyingTimesException(Exception):
    pass


class PanicBuyingTimes(object):
    def __init__(self, date_times, before_seconds=2, after_seconds=2,
                 false_sleep_second_randint=None, true_sleep_second=None,
                 debug=True, time_diff_ms=None):
        self.before_seconds = int(before_seconds)
        self.before_milliseconds = int(before_seconds * 1000 % 1000)
        self.after_seconds = int(after_seconds)
        self.after_milliseconds = int(after_seconds * 1000 % 1000)
        self.time_diff_ms = time_diff_ms or 0
        self.debug = debug
        self.false_sleep_second_randint = false_sleep_second_randint or (0, 0)
        self.true_sleep_second = true_sleep_second or 0
        self.date_times_queue = Queue.Queue()
        if isinstance(date_times, str):
            date_times = [date_times]
        date_times = self._make_correct_date_times(date_times)
        date_times = self.make_date_times(date_times)
        self._remove_expired_times(date_times)
        self._cache_data = {'start_print_false_count': 0}
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
            milliseconds = self.time_diff_ms + self.before_milliseconds
            if milliseconds > 0:
                start_date_time += datetime.timedelta(milliseconds=self.time_diff_ms)
            else:
                time_diff_ms = -self.time_diff_ms
                start_date_time -= datetime.timedelta(milliseconds=time_diff_ms)
            if date_time > now:
                end_date_time = date_time + datetime.timedelta(
                    seconds=self.after_seconds, milliseconds=self.time_diff_ms)
                milliseconds = self.time_diff_ms + self.after_milliseconds
                if milliseconds > 0:
                    end_date_time += datetime.timedelta(milliseconds=self.time_diff_ms)
                else:
                    time_diff_ms = -self.time_diff_ms
                    end_date_time -= datetime.timedelta(milliseconds=time_diff_ms)
                new_date_times.append([start_date_time, end_date_time])
        date_times = sorted(new_date_times, key=lambda x: x[0])
        for date_time in date_times:
            self.date_times_queue.put(date_time)

    @property
    def is_start(self):
        _is_start = self._start()
        if _is_start:
            if self.debug:
                print "IS_START: True",
                if self.true_sleep_second:
                    time.sleep(self.true_sleep_second)
                    print " | Sleep Time: {}s".format(self.true_sleep_second),
                print ''
            return True
        else:
            sleep_time = random.randint(*self.false_sleep_second_randint)
            if self.debug:
                print "IS_START: False | Sleep Time: {}s".format(sleep_time)
            for _ in xrange(sleep_time * 10):
                time.sleep(0.1)
                _is_start = self._start()
                if _is_start:
                    return True
            return False

    def _start(self):
        debug = self.debug
        now = datetime.datetime.now()
        start_time, end_time = self.this_time
        if start_time <= now <= end_time:
            if debug:
                print "IS_START: True | [{}] == [{}]".format(
                    start_time, now.strftime("%Y-%m-%d %H:%M:%S:%f"))
            return True
        if now >= end_time:
            try:
                self.this_time = self.date_times_queue.get(block=False)
            except Queue.Empty:
                raise PanicBuyingTimesException('Error: Had not times to wait !')
        if debug:
            if self._cache_data['start_print_false_count'] > 20:
                print "IS_START: False | [{}] == [{}]".format(
                    start_time, now.strftime("%Y-%m-%d %H:%M:%S:%f"))
                self._cache_data['start_print_false_count'] = 0
            else:
                self._cache_data['start_print_false_count'] += 1
        return False


if __name__ == '__main__':
    a = PanicBuyingTimes(['10:40:00', '2020-07-15 10:06:00'],
                         false_sleep_second_randint=(60, 70),
                         true_sleep_second=0.01)
    while True:
        now = datetime.datetime.now()
        if a.is_start:
            print "T - {}".format(now)
        else:
            print "F - {}".format(now)
        # time.sleep(1)
