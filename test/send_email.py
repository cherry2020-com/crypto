#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import time
from utils.send_email import Email

email = Email('minglei_weng@163.com', 'Wml93640218', 'weijiao.li@veeva.com',
              u'Code Review 邀请')
html = """\
<html>
  <head></head>
  <body>
    <p>Hi! 快来 Review ~~~ </p>
    <a href='https://gitlab.veevadev.com/veevaorion/chinasfa/merge_requests/812/diffs'>https://gitlab.veevadev.com/veevaorion/chinasfa/merge_requests/812/diffs</a>
  </body>
</html>
"""
while True:
    email.send(html)
    time.sleep(60)
