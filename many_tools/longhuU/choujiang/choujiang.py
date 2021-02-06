#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import os
import sys
from datetime import datetime
sys.path.extend(['/data/coding/my_tools/'])
from utils.buying_times import PanicBuyingTimes, PanicBuyingTimesException
from utils.fiddler import RawToPython, FiddlerRequestException

imp_templ = u'\033[1;33;44m{}\033[0m'


def rrr(file_name):
   rtp = RawToPython(file_name)
   rtp.set_param(req_param={'combinedId': '1987',
                            'componentId': 'mod_1611911779711',
                            'wheelId': '9718654f621811ebb7c87cd30adaf108'})
   print os.path.basename(file_name), rtp.requests().text


if __name__ == '__main__':
   parent_path = os.path.dirname(os.path.abspath(__file__))
   file_names = [
      '13511004353.txt',
      '15578801243.txt',
      '15578872074.txt',
      '17600196974.txt',
      # '18842670608.txt',
      '17601605665.txt',
      '18841164712.txt',
      '15369204212.txt',
   ]
   for file_name in file_names:
      rrr(os.path.join(parent_path, file_name))
