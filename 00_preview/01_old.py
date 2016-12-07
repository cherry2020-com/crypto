#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/12/5 0005"
"""
def old_fib(n):
    res = [0] * n
    index = 0
    a = 0
    b = 1
    while index < n:
        res[index] = b
        a, b = b, a + b
        index += 1
    return res

for fib_res in old_fib(20):
    print(fib_res)