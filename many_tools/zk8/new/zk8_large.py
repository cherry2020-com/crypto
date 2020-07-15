#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import sys
import os

import re
import urllib3
import time
from bs4 import BeautifulSoup

sys.path.extend(['/data/my_tools_env/my_tools/'])

from utils import pusher
from utils.fiddler import RawToPython


urllib3.disable_warnings()
CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def get_web_data(break_names=None):
    raw = RawToPython(os.path.join(CUR_DIR, 'zk8_large_head.txt'))
    try:
        web_data = raw.requests(timeout=10)
    except Exception:
        return {}, break_names
    result = {}
    if web_data and web_data.status_code == 200:
        soups = BeautifulSoup(web_data.text, "html5lib")
        soups.find_all('a',
                       href=re.compile(r'http://www\.zuanke8\.com/(thread|forum)-.+'),
                       target='_blank')
        new_break_names = []
        set_break_names = set(break_names or [])
        for tag in soups.find(id='alist').find_all('li'):
            text = tag.text.strip().split()
            if text:
                name = ' || '.join(text[:-1])
                if name in set_break_names:
                    break
                else:
                    new_break_names.append(name)
                url = "http://www.zuanke8.com/" + tag.a.attrs['href'] + "&mobile=no"
                # print name, url
                print ",",
                result[name] = url
        new_break_names.extend(break_names)
    else:
        new_break_names = break_names
    return result, new_break_names[:20]


def send_push(content, url):
    my_source = 's-70924c26-f3a5-4292-ad29-fb1b5877'
    receiver_source = 'g-85ed11d8-f448-4e41-bc1c-0e600f94'
    title = 'zk8'
    sound = 'default'
    pusher.send(my_source, receiver_source, title=title, url=url,
                content=content, sound=sound)


if __name__ == '__main__':
    break_names = []
    key_messages = [u'水', u'神', u'秒到', u'速度', u'速领', u'速撸', u'万家', u'毛',
                    u'好价', u'利器', u'又有了', u'又来了',
                    u'免费', u'斐讯', u'0元', u'零元', u'〇元', u'震惊', u'优惠券', u'1元',
                    u'一元', u'超级返', u'线报', u'高返', u'高反', u'有货', u'手慢无',
                    u'白菜', u'免单', u'漏洞',
                    'wj', 'bug', 'fx']
    exclude_key_messages = [u'赚神', u'求', u'有没有', u'吗', '?', u'？']
    while True:
        result, break_names = get_web_data(break_names)
        for title, url in result.iteritems():
            if_title = title.replace(' ', '').lower()
            for k in key_messages:
                if k in if_title:
                    for ek in exclude_key_messages:
                        if ek in if_title:
                            break
                    else:
                        send_push(u'[ZK8]' + title, url)
                    break
        time.sleep(5)
        print "."
        sys.stdout.flush()
