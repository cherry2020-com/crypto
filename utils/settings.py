#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/10/15 0014"
"""
import logging
import os

import sys

SDK_DIR = os.path.dirname(os.path.abspath(__file__))

# Email
# Sender = "TX_Warning@163.com"
Email_Sender = "Yun_Warning@163.com"
Email_Passwd = "Wml93640218"
Email_Receiver = "645008699@qq.com"
Email_Title = "Game Warning !!!"

# Log
Log_Name = "Run.log"
# Log_Format = "<%(levelname)s>: %(asctime)s --> %(message)s"
Log_Format = "<%(levelname)s>| %(message)s"
logging.getLogger("requests").setLevel(logging.ERROR)
logging.basicConfig(
    # filename=Log_Name,
    stream=sys.stdout,
    level=logging.DEBUG,
    format=Log_Format)
