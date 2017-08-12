#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import smtplib
from email.mime.text import MIMEText

import logging


class Email(object):
    log = logging.getLogger('utils.send_email.Email')

    def __init__(self, sender, password, receiver, title='My Tools Send E-mail'):
        host = 'smtp.163.com'
        port = 25
        self.title = title
        self.sender = sender
        self.password = password
        self.receiver = receiver
        self.host = host
        self.port = port

    def send(self, body, title=None):
        msg = MIMEText(body, 'html')
        msg['from'] = self.sender
        msg['to'] = self.receiver
        msg['subject'] = title or self.title
        server = smtplib.SMTP(self.host, self.port)
        server.starttls()
        server.login(self.sender, self.password)
        server.sendmail(self.sender, self.receiver, msg.as_string())
        result_info = 'The mail named <%s> to <%s> is sended successly.' % (
            title, self.receiver)
        self.log.info(result_info)
