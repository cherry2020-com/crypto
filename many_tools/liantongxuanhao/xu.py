#!/usr/bin/python
# -*- coding: UTF-8 -*-
with open('./output/xuanhao.txt') as f:
    fd = f.read()
# 15542552150
# 15542562550
# 13238039332

haomas = fd.split('\n')
from collections import Counter
# need_count = 5
# for x in haomas:
#     for hao, shu in Counter(x[1:]).items():
#         if shu >= need_count and hao != '4' :
#             print "{}->{}".format(hao, x)

# c = None
# for x in haomas:
#     c = x[0]
#     ct = 0
#     for i in x[1:]:
#         if c == i:
#             ct
# i_c = 0
# for x in haomas:
#     for i in x[2:]:
#         c = x[i_c + 1]
#         if c == i and c == x[i_c + 1]:
#             print x
#         i_c += 1
xunhuan = 3

for x in haomas:
    for index in range(len(x)):
        short_x = x[index: index + xunhuan]
        if len(short_x) != xunhuan:
            break
        is_diff = False
        for each_short_index in range(xunhuan-1):
            if short_x[each_short_index] != short_x[each_short_index+1]:
                is_diff = True
                break
        if not is_diff:
            print x
