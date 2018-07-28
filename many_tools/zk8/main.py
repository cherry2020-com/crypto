#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import sys
import os
import urllib3
import time
from bs4 import BeautifulSoup

sys.path.extend(['/data/my_tools_env/my_tools/'])

from utils import pusher
from utils.fiddler import RawToPython


urllib3.disable_warnings()
CUR_DIR = os.path.dirname(os.path.abspath(__file__))


def get_web_data(break_names=None):
    raw = RawToPython(os.path.join(CUR_DIR, 'z8_new_list_head.txt'))
    try:
        web_data = raw.requests(timeout=10)
    except Exception:
        return {}, break_names
    result = {}
    if web_data.status_code == 200:
        soups = BeautifulSoup(web_data.text, "lxml")
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
                url = "http://www.zuanke8.com/" + tag.a.attrs['href']
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
    key_messages = [u'水', u'秒到', u'速度', u'速领', u'万家', u'毛', u'好价', 'wj', 'bug']
    while True:
        result, break_names = get_web_data(break_names)
        for title, url in result.iteritems():
            if_title = title.replace(' ', '').lower()
            for k in key_messages:
                if k in if_title:
                    send_push(title, url)
                    break
        time.sleep(5)
        print "."
        sys.stdout.flush()
