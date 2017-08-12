#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import logging
import os

import sys

GOLD_DIR = os.path.dirname(os.path.abspath(__file__))

# Log
Log_Name = os.path.join(GOLD_DIR, "Run.log")
# Log_Format = "<%(levelname)s>: %(asctime)s --> %(message)s"
Log_Format = "<%(levelname)s>| %(message)s"
logging.getLogger("requests").setLevel(logging.ERROR)
logging.basicConfig(
    filename=Log_Name,
    # stream=sys.stdout,
    level=logging.DEBUG,
    format=Log_Format)
