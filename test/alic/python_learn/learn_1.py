#!/usr/bin/python
# -*- coding: UTF-8 -*-


def a():
    print '12345'


class Alic:
    _class = '_class'
    
    def __init__(self, *args):
        self._list = list(args)

    def __str__(self):
        return str(self._list)

    def __len__(self):
        return len(self._list)

    # def __repr__(self):
    #     return "Alic String"

    def __add__(self, other):
        self._list.append(other)
        return self._list

    def _my_month(self):
        return "1m", self._list

    def __my_month(self):
        return "2m"
    
    @classmethod
    def my_class(cls):
        return "my_class", cls._class

    @staticmethod
    def my_staticmethod():
        return "my_staticmethod", Alic._class





if __name__ == '__main__':
    a = Alic(1, 2, 3, 4, 5)
    print a._my_month()
    # print str(a)
    # print len(a)
    # a = a + 6
    # print str(a)
    # print Alic.my_class()
    # print Alic.my_staticmethod()
