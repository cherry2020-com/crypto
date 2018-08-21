#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import logging

import datetime

from utils import pusher
from utils.send_email import Email


def send_error_msg_by_email(msg):
    email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com',
                  'Script Error')
    try:
        email.send("{time}: {msg}".format(time=datetime.datetime.now(), msg=msg))
    except Exception as e:
        error_msg = "EmailError: {msg}: {e}".format(msg=msg, e=e)
        logging.error(error_msg)


def send_push(content, url, my_source, receiver_source, title, sound='default'):
    try:
        pusher.send(my_source, receiver_source, title=title, url=url,
                    content=content, sound=sound, auto_retry=True)
    except Exception as e:
        error_msg = u"PusherError: {title}: {e}".format(title=title, e=e)
        logging.error(error_msg)
        try:
            email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com',
                          'Script Error')
            email.send(title + str(e))
        except Exception as e:
            error_msg = u"EmailError: PusherError: {title}: {e}".format(title=title, e=e)
            logging.error(error_msg)


def send_email(title, content):
    email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com', title)
    try:
        email.send(content)
    except Exception as e:
        error_msg = "EmailError: {msg}: {e}".format(msg=title, e=e)
        logging.error(error_msg)
