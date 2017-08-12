#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import logging

ALL_SIM_CARDS = {
    '18842670608': {'port': '/dev/ttyUSB0', 'baudrate': 115200, 'pin': None},
    # '17084142906': {'port': '/dev/ttyUSB2', 'baudrate': 115200, 'pin': None},
}

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
