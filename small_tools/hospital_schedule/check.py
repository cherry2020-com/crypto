import os
import random
import time

from small_tools.hospital_schedule import APP_ACCESS_TOKEN, FILE_PATH, SLOW_TIMEOUT
from utils.fiddler_session import RawToPython


def check_card_no(is_one=True):
    head = os.path.join(FILE_PATH, 'getCurrentCardNo.txt')
    req = RawToPython(head)
    req.set_param(req_param={"app_access_token": APP_ACCESS_TOKEN})
    while True:
        try:
            req_json = req.requests(timeout=SLOW_TIMEOUT).json()
            print req_json
        except Exception as e:
            print '--> request error', e
        if is_one:
            break
        time.sleep(random.randint(5, 6))


if __name__ == '__main__':
    check_card_no(is_one=False)