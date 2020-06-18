#!/usr/bin/python
# -*- coding: UTF-8 -*-
from collections import Counter


def chongfu(numbers, need_count):
    for x in numbers:
        for hao, shu in Counter(x[1:]).items():
            if shu >= need_count:
                print "{}->{}".format(hao, x)


def lianxuchongfu(numbers, need_count=3):
    for x in numbers:
        for index in range(len(x)):
            short_x = x[index: index + need_count]
            if len(short_x) != need_count:
                break
            is_diff = False
            for each_short_index in range(need_count-1):
                if short_x[each_short_index] != short_x[each_short_index+1]:
                    is_diff = True
                    break
            if not is_diff:
                print x


def baohan(numbers, baohan):
    for x in numbers:
        if baohan in x:
            print '{}-->{}'.format(baohan, x)


if __name__ == '__main__':
    with open('./xuanhao.txt') as f:
        fd = f.read()
    haomas = fd.split('\n')
    # chongfu(haomas, 5)
    # lianxuchongfu(haomas, 4)
    baohan(haomas, '0218')