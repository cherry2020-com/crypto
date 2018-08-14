#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import logging

from utils import pusher
from utils.send_email import Email


def send_push(content, url, my_source, receiver_source, title, sound='default'):
    try:
        pusher.send(my_source, receiver_source, title=title, url=url,
                    content=content, sound=sound)
    except Exception as e:
        logging.error("PusherError: " + title + ': ' + str(e))
        try:
            email = Email('Yun_Warning@163.com', 'Wml93640218', '645008699@qq.com',
                          'Script Error')
            email.send(str(e))
        except Exception as e:
            logging.error("EmailError: PusherError: " + title + ': ' + str(e))