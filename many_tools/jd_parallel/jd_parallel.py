#!/usr/bin/python
# -*- coding: UTF-8 -*-
from utils import fiddler_session


class JDParallel(object):

    def __init__(self, search_url, name_keyword=None, discount_keyword=None):
        self.search_url = search_url
        self.name_keyword = name_keyword
        self.discount_keyword = discount_keyword

    def _get_goods(self):
        fiddler_session.RawToPython

    def process(self):
        self._get_goods()