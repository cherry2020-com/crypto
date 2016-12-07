#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/12/5 0005"
"""
def fib(n):
    index = 0
    a = 0
    b = 1
    while index < n:
        yield b
        a, b = b, a + b
        index += 1
        print('-'*10 + 'test yield fib' + '-'*10)
# for fib_res in fib(20):
#   print(fib_res)


def h():
    print('Wen Chuan'),
    m = yield 5  # Fighting!
    print(m)
    d = yield 12
    print('We are together!')

c = h()
m = next(c)  #m 获取了yield 5 的参数值 5
d = c.send('Fighting!')  #d 获取了yield 12 的参数值12
print('We will never forget the date', m, '.', d)