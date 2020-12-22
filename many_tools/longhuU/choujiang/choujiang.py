#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import sys
from datetime import datetime

from utils.buying_times import PanicBuyingTimes, PanicBuyingTimesException
from utils.fiddler import RawToPython, FiddlerRequestException

imp_templ = u'\033[1;33;44m{}\033[0m'

if __name__ == '__main__':
   rtp = RawToPython('./13511004353.txt')
   print '13511004353', rtp.requests().text
   rtp = RawToPython('./15578801243.txt')
   print '15578801243', rtp.requests().text
   rtp = RawToPython('./15578872074.txt')
   print '15578872074', rtp.requests().text
   rtp = RawToPython('./17600196974.txt')
   print '17600196974', rtp.requests().text
   rtp = RawToPython('./18842670608.txt')
   print '18842670608', rtp.requests().text
   rtp = RawToPython('./17601605665.txt')
   print '17601605665', rtp.requests().text
   rtp = RawToPython('./18841164712.txt')
   print '18841164712', rtp.requests().text
   rtp = RawToPython('./15369204212.txt')
   print '15369204212', rtp.requests().text
