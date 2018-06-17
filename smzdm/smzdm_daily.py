#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import random
import sys
import requests
import re

import time

COMMON_PASSWORD = 'Wml93640218.'

SMZDM_ACCOUNTS = [
    {'USERNAME': '15578801243', 'PASSWORD': COMMON_PASSWORD},  # 风险账号
    {'USERNAME': '15578872074', 'PASSWORD': COMMON_PASSWORD},
    {'USERNAME': '17810358585', 'PASSWORD': COMMON_PASSWORD},
    {'USERNAME': '18410909019', 'PASSWORD': COMMON_PASSWORD},
    {'USERNAME': '13511004353', 'PASSWORD': COMMON_PASSWORD},
    {'USERNAME': '13840897934', 'PASSWORD': COMMON_PASSWORD},
    {'USERNAME': '17084142906', 'PASSWORD': COMMON_PASSWORD},
    {'USERNAME': '17084142981', 'PASSWORD': COMMON_PASSWORD},
    {'USERNAME': '17600196974', 'PASSWORD': COMMON_PASSWORD},  # 风险账号
    # {'USERNAME': '17180128020', 'PASSWORD': COMMON_PASSWORD},
    # {'USERNAME': '17180128060', 'PASSWORD': COMMON_PASSWORD},
    # {'USERNAME': '17180128689', 'PASSWORD': COMMON_PASSWORD},  # 风险账号
    {'USERNAME': '18842670608', 'PASSWORD': COMMON_PASSWORD},
    {'USERNAME': '15010785631', 'PASSWORD': '1q2w3e4r'},
    {'USERNAME': '17600946098', 'PASSWORD': '1q2w3e4r'},
    {'USERNAME': '18842624282', 'PASSWORD': '1q2w3e4r'},
]


class SMZDMDailyException(Exception):
    def __init__(self, req):
        self.req = req

    def __str__(self):
        return str(self.req)


class SMZDMDaily(object):
    BASE_URL = 'https://zhiyou.smzdm.com'
    LOGIN_URL = BASE_URL + '/user/login/ajax_check'
    CHECKIN_URL = BASE_URL + '/user/checkin/jsonp_checkin'

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()

    def checkin(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:20.0) Gecko/20100101 Firefox/20.0',
            'Host': 'zhiyou.smzdm.com',
            'Referer': 'http://www.smzdm.com/'
        }

        params = {
            'username': self.username,
            'password': self.password,
        }

        r = self.session.get(self.BASE_URL, headers=headers, verify=True)
        r = self.session.post(self.LOGIN_URL, data=params, headers=headers, verify=True)
        r = self.session.get(self.CHECKIN_URL, headers=headers, verify=True)
        if r.status_code != 200:
            raise SMZDMDailyException(r)

        data = r.text
        jdata = json.loads(data)

        return jdata


if __name__ == '__main__':
    if SMZDM_ACCOUNTS:
        usernames = {x['USERNAME'] for x in SMZDM_ACCOUNTS}
        assert len(usernames) == len(SMZDM_ACCOUNTS)
        print(u'%s account waiting for sign in !' % len(usernames))

    for account in SMZDM_ACCOUNTS:
        try:
            smzdm = SMZDMDaily(account['USERNAME'], account['PASSWORD'])
            result = smzdm.checkin()
        except SMZDMDailyException as e:
            print('Fail', e)
        except Exception as e:
            print('Fail', e)
        else:
            if isinstance(result, dict):
                msg = result.get('data', {}).get('slogan', '')
            else:
                msg = result
            print(u'Successful: {} - {}'.format(
                account['USERNAME'], re.sub(r'<.*?>', '', msg)))
        sleep_s = random.randint(5, 10)
        print ('%s s' % sleep_s)
        time.sleep(sleep_s)
