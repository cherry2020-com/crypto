#!/usr/bin/python
# -*- coding: UTF-8 -*-
import json
import os.path

from small_tools.hospital_schedule import *
from utils.fiddler_session import RawToPython

imp_templ = u'\033[1;33;44m{}\033[0m'

fast_timeout = 1 or FAST_TIMEOUT


def submit(department_id, doctor_id, good_time):
    if good_time is None:
        print u'--> 没有可预约的时间, 终止请求'
        return 'none'
    if IS_DEBUG_SUBMIT:
        head = os.path.join(FILE_PATH, 'fake_submit.txt')
    else:
        head = os.path.join(FILE_PATH, 'submit.txt')
    req = RawToPython(head)
    body_data = json.loads(req.body_data['data'])
    body_data['hasCard'] = "1" if HAS_CARD else "0"
    body_data['deptCode'] = "2237"
    body_data['doctorId'] = "1222"
    body_data['date'] = DATE
    body_data['time'] = good_time['time']
    body_data['roomId'] = good_time['roomId']
    body_data['timeIndexNo'] = good_time['timeIndexNo']
    body_data['deptName'] = DEPARTMENT
    body_data['doctorName'] = DOCTOR
    req.set_param(req_param={"data": json.dumps(body_data)})
    try:
        req_data = req.requests(timeout=fast_timeout)
        req_json = req_data.json()
        status_code = int(req_json['status'])
        if status_code == 200:
            print imp_templ.format(u'--> 成功抢到，请检查预')
            return 'success'
        elif status_code == 500:
            msg = req_json.get('responseMessage', '')
            if u'不能重复预约' in msg:
                print imp_templ.format(u'--> 成功抢到，请检查预')
                return 'success'
            print u'--> 未能抢到: ', req_json.get('responseMessage')
            return 'fail'
        print '--> submit: what?: ', req_json
        return 'what?'
    except Exception as e:
        print u'--> 抢注报错: ', e
        return 'error'


if __name__ == '__main__':
    path = os.path.join(FILE_PATH, 'liyingList.json')
    with open(path) as f:
        li_json = json.loads(f.read())
    while True:
        for good_time in li_json['result']['doctorDateTimeList']:
            _type = submit("2237", "1222", good_time)
            if _type == 'success':
                break
