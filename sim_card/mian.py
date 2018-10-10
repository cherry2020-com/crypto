# !/usr/bin/env python
# - * - encoding: UTF-8 - * -
from __future__ import print_function

import datetime
import logging
import time

from sim_card.gsmmodem import GsmModem
from sim_card.gsmmodem.exceptions import InterruptedException, CommandError
from sim_card.settings import ALL_SIM_CARDS
from utils import tools


def send_push(title, url, t_type):
    tools.send_push(
        u'[{}]'.format(t_type) + title, url,
        's-e4ad6ffd-6890-493d-8056-119717e2',
        'g-e0657ee7-1384-49a7-a828-55b9fcfa',
        t_type)


class SimCard(object):
    sms_format = u"{text} | {number} | {time}"
    call_format = u"{number} | {time} | {ring_count}"

    def __init__(self, port='/dev/ttyUSB0', baudrate=115200, pin=None):
        self.modem = GsmModem(port, baudrate,
                              smsReceivedCallbackFunc=SimCard.callback_sms,
                              incomingCallCallbackFunc=SimCard.callback_call,
                              smsStatusReportCallback=SimCard.callback_sms_status)
        self.modem.smsTextMode = True
        self.modem.connect(pin)

    def join(self, timeout=None):
        self.modem.rxThread.join(timeout)

    def close(self):
        self.modem.close()

    def call(self, number, timeout=50):
        self.modem.dial(number,
                        callStatusUpdateCallbackFunc=SimCard.callback_call_status)
        try:
            self.join(timeout)
        except Exception as e:
            logging.error('Call to [%s] timeout.' % number)
            # self.close()

    @staticmethod
    def callback_sms(sms, *args, **kwargs):
        msg = SimCard.sms_format.format(
            number=sms.number, time=sms.time, text=sms.text)
        send_push(msg, msg, 'SMS')

    @staticmethod
    def callback_call(call, *args, **kwargs):
        if call.ringCount == 1:
            logging.info('Incoming call from: %s' % call.number)
            msg = SimCard.call_format.format(
                number=call.number, time=datetime.datetime.now(),
                ring_count=call.ringCount)
            send_push(msg, msg, 'CALL')
        if call.ringCount >= 10:
            msg = SimCard.call_format.format(
                number=call.number, time=datetime.datetime.now(),
                ring_count=call.ringCount)
            send_push(msg, msg, 'CALL')
            if call.dtmfSupport:
                logging.info('Answer number: [%s]' % call.number)
                call.answer()
                time.sleep(2.0)
                try:
                    call.sendDtmfTone('9515999955951')
                    time.sleep(10.0)
                except InterruptedException as e:
                    # Call was ended during playback
                    logging.error('DTMF playback interrupted: {0} ({1} Error {2})'.format(
                        e, e.cause.type, e.cause.code))
                finally:
                    if call.answered:
                        logging.info('Hanging up call.')
                        call.hangup()
            else:
                logging.info('Modem has no DTMF support - hanging up call.')
                call.hangup()
        else:
            logging.info('Call from {0} is still ringing...'.format(call.number))

    @staticmethod
    def callback_sms_status(sms, *args, **kwargs):
        pass

    @staticmethod
    def callback_call_status(call, *args, **kwargs):
        logging.info('Call status update callback function called')
        if call.answered:
            logging.info('Call has been answered; waiting a while...')
            time.sleep(3.0)
            try:
                if call.active:
                    call.sendDtmfTone('9515999955951')
                    time.sleep(10.0)
            except InterruptedException as e:
                # Call was ended during playback
                logging.info('DTMF playback interrupted: {0} ({1} Error {2})'.format(
                    e, e.cause.type, e.cause.code))
            except CommandError as e:
                logging.error('DTMF playback failed: {0}'.format(e))
            finally:
                if call.active:  # Call is still active
                    logging.info('Hanging up call...')
                    call.hangup()
        else:
            # Call is no longer active (remote party ended it)
            logging.info('Call has been ended by remote party')


ALL_GSM = {'17084140000', SimCard('/dev/tty.usbserial')}


def get_all_gsm():
    global ALL_GSM
    for number, config in ALL_SIM_CARDS.items():
        ALL_GSM[number] = SimCard(**config)


def join_all_gsm():
    for number, gsm_object in ALL_GSM.items():
        gsm_object.join()
        logging.info('joined gsm: [%s]' % number)


def close_all_gsm():
    for number, gsm_object in ALL_GSM.items():
        gsm_object.close()
        logging.info('closed gsm: [%s]' % number)


if __name__ == '__main__':
    get_all_gsm()
    try:
        join_all_gsm()
    finally:
        close_all_gsm()
