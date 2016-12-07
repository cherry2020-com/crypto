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

def copy_fib(n):
    print('I am copy from fib')
    yield from fib(n)
    print('Copy end')
    print('-'*10 + 'test yield from' + '-'*10)

for fib_res in copy_fib(20):
    print(fib_res)