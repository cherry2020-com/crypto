#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import logging

import datetime

from utils import pusher
from utils.send_email import Email


def send_push(content, url, my_source, receiver_source, title, sound='default'):
    try:
        pusher.send(my_source, receiver_source, title=title, url=url,
                    content=content, sound=sound, auto_retry=True)
    except Exception as e:
        error_msg = "{time}: PusherError: {title}: {e}".format(
            time=datetime.datetime.now(), title=title, e=e)
        logging.error(error_msg)
        try:
            email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com',
                          'Script Error')
            email.send(title + str(e))
        except Exception as e:
            error_msg = "{time}: EmailError: PusherError: {title}: {e}".format(
                time=datetime.datetime.now(), title=title, e=e)
            logging.error(error_msg)