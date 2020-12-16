#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import json
import re
import sys
from datetime import datetime

sys.path.extend(['D:/Coding/my_tools/'])
sys.path.extend(['/Users/mingleiweng/Coding/Coding/my_tools'])

from utils.buying_times import PanicBuyingTimes, PanicBuyingTimesException
from utils.fiddler_session import RawToPython, FiddlerRequestException

imp_templ = u'\033[1;33;44m{}\033[0m'


QUANDATA_RTP = RawToPython('./quandata.txt')


def get_data():
    global QUANDATA_RTP
    rtp_text = QUANDATA_RTP.requests().text
    data = re.findall(r'var entity = (.*)', rtp_text)
    data_json = json.loads(data[0])
    for each in json.loads(data_json['collocationData'])['data']:
        try:
            each = each['data']['prizes'][0]
            each['prizeName']
        except:
            continue
        if each['prizeName'] == u'50元必抢神券':
            result = {'activityId': each['ruleId'], 'activityPrizeId': each['rulePrizeId']}
            print '-->', result
            return result


if __name__ == '__main__':
    file_path = sys.argv[1]
    date_times = "2020-12-17 14:00:00"
    # time_diff_ms = get_time_diff()
    # print '-->time_diff_ms', time_diff_ms
    date_times = sys.argv[2] if len(sys.argv) == 3 else date_times
    buying_time = PanicBuyingTimes(date_times, before_seconds=2,
                                   after_seconds=3,
                                   false_sleep_second_randint=(60, 120),
                                   debug=True, time_diff_ms=None)
    req = RawToPython(file_path)
    data = get_data()
    req.set_param(req_param=data)
    count = 0
    heart_count = 1
    while True:
        try:
            if buying_time.is_start:
                print '--> START !!!', datetime.now()
                web_data = req.requests(timeout=5)
                # web_data = req.requests(timeout=0.5)
                print imp_templ.format(web_data.json())
            else:
                try:
                    data = get_data()
                    req.set_param(req_param=data)
                    web_data = req.requests(timeout=5)
                    print imp_templ.format(web_data.json())
                except FiddlerRequestException:
                    pass
        except PanicBuyingTimesException as e:
            print '-->ERROR:PanicBuyingTimesException:', e
            break
        except Exception as e:
            print '-->ERROR:Exception:', e
        sys.stdout.flush()
