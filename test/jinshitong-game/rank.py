#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import re

import time

from utils.fiddler import RawToPython

raw = RawToPython('h.txt')

def main():
    w_d = raw.requests()
    # print w_d.text
    ls = re.findall(r'>(.\d+.*?)<.+?(\d+.*?)<', w_d.text)
    f_s = []
    z_s = {}
    for l in ls[:3]:
        f = re.findall(r'\d+', l[0])[0]
        f_s.append(f)
        r = re.findall(r'\d+', l[1])[0]
        z_s[f] = r

    f_s.sort(reverse=True)
    i_s = {0: 5000, 1: 3000, 2: 2000}
    for i, f in enumerate(f_s):
        print u"{}, {}分, {}人, {:.2f}元".format(i+1, f, z_s[f], i_s[i]/float(z_s[f]))
    print ''

while True:
    main()
    time.sleep(3)
