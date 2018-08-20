#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import datetime
import time


class PanicBuyingTimesException(Exception):
    pass


class PanicBuyingTimes(object):
    def __init__(self, date_times, before_seconds=3, after_seconds=8):
        self.before_seconds = before_seconds
        self.after_seconds = after_seconds
        if isinstance(date_times, str):
            date_times = [date_times]
        self.date_times = self._make_correct_date_times(date_times)
        self.date_times = self.make_date_times(self.date_times)
        self._remove_expired_times()
        self.this_time = self.date_times.pop()

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

    def _remove_expired_times(self):
        now = datetime.datetime.now()
        new_date_times = []
        for date_time in self.date_times:
            start_date_time = date_time - datetime.timedelta(
                seconds=self.before_seconds)
            if date_time > now:
                end_date_time = date_time + datetime.timedelta(
                    seconds=self.after_seconds)
                new_date_times.append([start_date_time, end_date_time])
        self.date_times = sorted(new_date_times, key=lambda x: x[0], reverse=True)

    @property
    def is_start(self):
        return self.start()

    def start(self, debug=False, other_info=''):
        now = datetime.datetime.now()
        start_time, end_time = self.this_time
        if start_time <= now <= end_time:
            if debug:
                print "True - {} - {}".format(now.strftime("%Y-%m-%d %H:%M:%S"),
                                              other_info)
            return True
        if now >= end_time:
            try:
                self.this_time = self.date_times.pop()
            except IndexError:
                raise PanicBuyingTimesException('Error: Had not times to wait !')
        if debug:
            print "False - {} - {}".format(now.strftime("%Y-%m-%d %H:%M:%S"),
                                           other_info)
        return False


if __name__ == '__main__':
    a = PanicBuyingTimes(['18:18:00', '2018-07-15 09:52:00',
                          '15:25:00', '2018-08-15 22:28:00'])
    while True:
        now = datetime.datetime.now()
        if a.is_start:
            print "T - {}".format(now)
        else:
            print "F - {}".format(now)
        time.sleep(0.2)
