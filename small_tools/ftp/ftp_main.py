#!/usr/bin/python
# -*- coding: UTF-8 -*-

import tftpy

server = tftpy.TftpServer('./tftp-dir')
server.listen('0.0.0.0', 69)
