# -*- coding: UTF-8 -*-
import random
import re
import sys
import os
import time
import pickle
import traceback

import datetime

import func_timeout
from bs4 import BeautifulSoup


u"""
w13511001100 - 2580456W
zk_15578877887 - vXMJsWd2v9gq63Sk - 母亲的名字：XoMZFHu89U5sLMwa
zk_15578807880 - o8AV8S88w9nFup8j - 母亲的名字：0Z19wAedW5DlV4oY
zk_15578807881 - o8AV8S88w9nFup8j - 母亲的名字：0Z19wAedW5DlV4oY
zk_15578807882 - o8AV8S88w9nFup8j - 母亲的名字：0Z19wAedW5DlV4oY
"""
sys.path.extend(['/data/my_tools_env/my_tools/'])

from utils import tools
from utils.push_over import Pushover
from utils.fiddler_session import RawToPython, FiddlerRequestTimeOutException

CUR_DIR = os.path.dirname(os.path.abspath(__file__))


IS_KEYWORD_FILTER = True
NEW_NEW_SAVE_COUNT = 10
NEW_HOT_SAVE_COUNT = 3
NEW_MY_HOT_SAVE_COUNT = 5
NEW_MY_HOT_SEND_COMMENT_COUNT = 12
WAIT_HOT_COUNT = 6
MANY_HOT_TO_SEND_WITH_EMAIL_COUNT = 500


_NEW_HOT_COUNT = 0
_NEW_NEW_COUNT = 0
_NEW_MY_HOT_COUNT = 0

_GLOBAL_PUSHOVERS = {}


def test_print(*args, **kwargs):
    print args, kwargs

# tools.send_push = test_print


# 'http://www.zuanke8.com/forum.php?mod=viewthread&tid=5916448&extra=page%3D1&page=1&mobile=no'
# 'http://www.zuanke8.com/thread-5916448-1-1.html'


def change_url(uri):
    if '?' not in uri:
        tid = re.findall(r'-(\d+?)-1-1\.html', uri)[0]
        return 'http://www.zuanke8.com/forum.php?mod=viewthread&tid={}' \
               '&extra=page%3D1&page=1&mobile=no'.format(tid)
    need_str = ['mod=', 'tid=']
    uri_main, uri_others = uri.split('?')
    uri_others = uri_others.split('&')
    need_others = []
    for other in uri_others:
        for n in need_str:
            if other.startswith(n):
                need_others.append(other)
    need_others.append('mobile=no')
    if uri.startswith('http'):
        return uri_main + '?' + '&'.join(need_others)
    return 'http://www.zuanke8.com/' + uri_main + '?' + '&'.join(need_others)


def get_web_hot_data(request_raw, exist_titles=None):
    global _NEW_HOT_COUNT
    if exist_titles is None:
        with open(os.path.join(CUR_DIR, 'z8_exist_hot_titles.txt')) as f:
            exist_titles = pickle.load(f)
    try:
        web_data = request_raw.requests(timeout=10)
    except FiddlerRequestTimeOutException:
        print 'FiddlerRequestTimeOutException: get_web_hot_data'
        time.sleep(10)
        return {}, exist_titles
    except func_timeout.exceptions.FunctionTimedOut:
        print 'func_timeout.exceptions.FunctionTimedOut: get_web_hot_data'
        time.sleep(10)
        return {}, break_names
    except Exception as e:
        print 'Exception: get_web_hot_data'
        tools.send_error_msg_by_email("[zk8]get_web_data: " + traceback.format_exc())
        time.sleep(30)
        return {}, exist_titles
    exist_titles_set = set(exist_titles) if exist_titles else set()
    new_titles = []
    result = {}
    is_get_new = False
    if web_data and web_data.status_code == 200:
        soups = BeautifulSoup(web_data.text, "lxml")
        soup_find = soups.findAll(class_='dt valt')
        if not soup_find:
            return {}, exist_titles
        # assert len(soup_find) == 3
        hour_hots_keys = {0: '[6H]', 1: '[24H]', 2: '[48H]'}
        hour_hots_count = {}
        real_hour_hots_count = {}
        if len(soup_find) < 3:
            print "Hot_Web_Find-ERROR-[len(soup_find) < 3]"
            return {}, exist_titles
        for index, hour_hots in enumerate(soup_find):
            index_key = hour_hots_keys.get(index, '[xH]')
            hour_hots_count[index_key] = 0
            real_hour_hots_count[index_key] = 0
            all_hour_hots = list(hour_hots.findAll('td')) + list(hour_hots.findAll('th'))
            for hour_hot in all_hour_hots:
                if not hour_hot.a:
                    continue
                hour_hots_count[index_key] += 1
                text = hour_hot.text.strip().split()
                if text:
                    name = ' || '.join(text)
                    name = index_key + name
                    if name not in exist_titles_set:
                        result[name] = hour_hot.a.attrs['href']
                        is_get_new = True
                        new_titles.append(name)
                        real_hour_hots_count[index_key] += 1

        print "Hot_Web_Find-6h_%s-24h_%s-48h_%s-xh_%s|" % (
            hour_hots_count['[6H]'], hour_hots_count['[24H]'], hour_hots_count['[48H]'],
            hour_hots_count.get('[xH]', 0)),
        print "Hot_Real_Find-6h_%s-24h_%s-48h_%s-xh_%s|" % (
            real_hour_hots_count['[6H]'], real_hour_hots_count['[24H]'],
            real_hour_hots_count['[48H]'], real_hour_hots_count.get('[xH]', 0)),
    exist_titles_limit = (new_titles + exist_titles)[:1000]
    if is_get_new:
        _NEW_HOT_COUNT += len(result)
        if _NEW_HOT_COUNT > NEW_HOT_SAVE_COUNT:
            print "Hot_Saved-%s/%s|" % (_NEW_HOT_COUNT, NEW_HOT_SAVE_COUNT),
            _NEW_HOT_COUNT = 0
            with open(os.path.join(CUR_DIR, 'z8_exist_hot_titles.txt'), 'wb+') as f:
                pickle.dump(exist_titles_limit, f)
        else:
            print "Hot_Count-%s/%s|" % (_NEW_HOT_COUNT, NEW_HOT_SAVE_COUNT),
    return result, exist_titles_limit


def get_web_data(request_raw, break_names=None):
    global _NEW_NEW_COUNT
    if break_names is None:
        with open(os.path.join(CUR_DIR, 'z8_exist_new_titles.txt')) as f:
            break_names = pickle.load(f)
    try:
        web_data = request_raw.requests(timeout=10)
    except FiddlerRequestTimeOutException:
        print 'FiddlerRequestTimeOutException: get_web_data'
        time.sleep(10)
        return {}, break_names, None
    except Exception as e:
        print 'Exception: get_web_data'
        tools.send_error_msg_by_email("[zk8]get_web_data: " + traceback.format_exc())
        time.sleep(10)
        return {}, break_names, None
    result = {}
    is_get_new = False
    if web_data and web_data.status_code == 200:
        soups = BeautifulSoup(web_data.text, "lxml")
        new_break_names = []
        set_break_names = set(break_names or [])
        soup_find = soups.find(id='alist')
        if not soup_find:
            return {}, break_names, None
        print "New_Web_Find_%s|" % len(soup_find.find_all('li')),
        for tag in soup_find.find_all('li'):
            text = tag.a.h1.text.strip().split()
            if text:
                name = ' || '.join(text)
                if name in set_break_names:
                    break
                new_break_names.append(name)
                is_get_new = True
                result[name] = tag.a.attrs['href']
        print "New_Real_Find_%s|" % len(result),
        new_break_names.extend(break_names)
    else:
        new_break_names = break_names
    break_names = new_break_names[:50]
    if is_get_new:
        _NEW_NEW_COUNT += len(result)
        if _NEW_NEW_COUNT > NEW_NEW_SAVE_COUNT:
            print "New_Saved-%s/%s|" % (_NEW_NEW_COUNT, NEW_NEW_SAVE_COUNT),
            _NEW_NEW_COUNT = 0
            with open(os.path.join(CUR_DIR, 'z8_exist_new_titles.txt'), 'wb+') as f:
                pickle.dump(break_names, f)
        else:
            print "New_Count-%s/%s|" % (_NEW_NEW_COUNT, NEW_NEW_SAVE_COUNT),
    return result, break_names, web_data


def get_web_data_for_my_hot(request_raw, break_names=None, web_data=None):
    global _NEW_MY_HOT_COUNT
    if break_names is None:
        with open(os.path.join(CUR_DIR, 'z8_exist_my_hot_titles.txt')) as f:
            break_names = pickle.load(f)
    if web_data is None:
        try:
            web_data = request_raw.requests(timeout=10)
        except FiddlerRequestTimeOutException:
            print 'FiddlerRequestTimeOutException: get_web_data_for_my_hot'
            time.sleep(30)
            return {}, break_names
        except func_timeout.exceptions.FunctionTimedOut:
            print 'func_timeout.exceptions.FunctionTimedOut: get_web_data_for_my_hot'
            time.sleep(30)
            return {}, break_names
        except Exception as e:
            print 'Exception: get_web_data_for_my_hot'
            tools.send_error_msg_by_email(
                "[zk8]get_web_data_for_my_hot: " + traceback.format_exc())
            time.sleep(30)
            return {}, break_names
    result = {}
    is_get_new = False
    if web_data and web_data.status_code == 200:
        soups = BeautifulSoup(web_data.text, "lxml")
        new_break_names = []
        set_break_names = set(break_names or [])
        soup_find = soups.find(id='alist')
        if not soup_find:
            return {}, break_names
        for tag in soup_find.find_all('li'):
            text = tag.a.h1.text.strip().split()
            if text:
                name = ' || '.join(text)
                if name in set_break_names:
                    continue
                replies_count = tag.a.find(class_='replies').text
                replies_count = int(replies_count or 0)
                if replies_count < NEW_MY_HOT_SEND_COMMENT_COUNT:
                    continue
                new_break_names.append(name)
                is_get_new = True
                result[name] = tag.a.attrs['href']
        print "My_Hot_Real_Find_%s|" % len(result),
        new_break_names.extend(break_names)
    else:
        new_break_names = break_names
    break_names = new_break_names[:50]
    if is_get_new:
        _NEW_MY_HOT_COUNT += len(result)
        if _NEW_MY_HOT_COUNT > NEW_MY_HOT_SAVE_COUNT:
            print "My_Hot_Saved-%s/%s|" % (_NEW_MY_HOT_COUNT, NEW_NEW_SAVE_COUNT),
            _NEW_MY_HOT_COUNT = 0
            with open(os.path.join(CUR_DIR, 'z8_exist_my_hot_titles.txt'), 'wb+') as f:
                pickle.dump(break_names, f)
        else:
            print "My_Hot_Count-%s/%s|" % (_NEW_MY_HOT_COUNT, NEW_NEW_SAVE_COUNT),
    return result, break_names


CHANGE_MAPS = {u'〇': '0', u'零': '0', u'一': '1', u'二': '2', u'三': '3', u'四': '4',
               u'五': '5', u'六': '6', u'七': '7', u'八': '8', u'九': '9', u'十': '10',
               u'百': '100', u'千': '1000', u'万': '10000', u'０': '0', u'１': '1',
               u'２': '2', u'３': '3', u'４': '4', u'５': '5', u'６': '6', u'７': '7',
               u'８': '8', u'９': '9', u'壹': '1', u'贰': '2', u'叁': '3', u'肆': '4',
               u'伍': '5', u'陆': '6', u'柒': '7', u'捌': '8', u'玖': '9', u'拾': '10',
               u'佰': '100', u'仟': '1000', u'萬': '10000', u'亿': '100000000'}


def change_title(title):
    new_title = title.strip().replace(' ', '').replace('||', '').lower()
    for i in title:
        if i in CHANGE_MAPS:
            new_title = new_title.replace(i, CHANGE_MAPS[i])
    return new_title


def init():
    tools.send_push = test_print
    with open(os.path.join(CUR_DIR, 'z8_exist_new_titles.txt'), 'wb+') as f:
        pickle.dump([], f)
    with open(os.path.join(CUR_DIR, 'z8_exist_hot_titles.txt'), 'wb+') as f:
        pickle.dump([], f)


def custom_send_push(title, url):
    _key = 'zk8_new'
    if _key not in _GLOBAL_PUSHOVERS:
        _GLOBAL_PUSHOVERS[_key] = Pushover(_key)
    _GLOBAL_PUSHOVERS[_key].send(title, url=url, url_title=u'>> 详情链接 <<')


def custom_send_push_hot(title, url):
    _key = 'zk8_hot'
    if _key not in _GLOBAL_PUSHOVERS:
        _GLOBAL_PUSHOVERS[_key] = Pushover(_key)
    _GLOBAL_PUSHOVERS[_key].send(title, url=url, url_title=u'>> 详情链接 <<')


def custom_send_push_my_hot(title, url):
    _key = 'zk8_mhot'
    if _key not in _GLOBAL_PUSHOVERS:
        _GLOBAL_PUSHOVERS[_key] = Pushover(_key)
    _GLOBAL_PUSHOVERS[_key].send(title, url=url, url_title=u'>> 详情链接 <<')


if __name__ == '__main__':
    # init()
    enable_new = True
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'hot':
            enable_new = False
    print '--> ENABLE_NEW = {}'.format(enable_new)
    time_sleep = 5
    if len(sys.argv) >= 3:
        time_sleep = int(sys.argv[2][:-1])
    print '--> TIME_SLEEP = {}'.format(time_sleep)
    break_names = None
    my_hot_break_names = None
    hot_break_names = None
    important_key_messages = {'wj', 'bug', 'fx', u'10000家', u'斐讯', u"有水", u"水了",
                              u"大水", u"洪水", u"水到", u'好价', u'漏洞', u'黄金', u'洞',
                              u'首发', 'ruan', u'软件', u'速来', u'快去', u'手慢无',
                              u'神券', u'神卷', u'无门槛', u'毛', u'速度', u'速领', u'速撸',
                              u'好用', u'中了', u'转赠', u'货号'}
    key_messages = {u'神', u'券', u'卷', u'抢', u'立减',
                    u'防身', u'性价比', u'便宜', u'秒杀',
                    u'秒到', u'可以了', u'有货', u'防身',
                    u'利器', u'又有', u'来了', u'又1', u'免费', u'0元', u'震惊',
                    u'1元', u'9.9', u'9块9', u'9元', u'超级返', u'线报', u'高返',
                    u'高反', u'有货', u'活动', u'白菜', u'免单', u'到手', u'大妈',
                    u'美滋滋', u'果', u'菓', u'锅', u'整理', u'一抖'}
    exclude_key_messages = {u'求', u'有没有', u'吗', u'呢', u'么'}
    new_list_request_raw = RawToPython(os.path.join(CUR_DIR, 'z8_new_list_head.txt'))
    hot_list_request_raw = RawToPython(os.path.join(CUR_DIR, 'z8_hot_list_head.txt'))
    count = 1
    email_title = '[ZK8] Many Titles Need To Send By E-mail'
    email_msg_tmp = u"【{}】 - {}\r\n\r\n"
    while True:
        if enable_new:
            result, break_names, web_data = get_web_data(new_list_request_raw,
                                                         break_names)
            if IS_KEYWORD_FILTER:
                for title, uri in result.iteritems():
                    if_title = change_title(title)
                    for i_k in important_key_messages:
                        if i_k in if_title:
                            custom_send_push('[x]' + title, change_url(uri))
                            print ">>Send_Important_New|",
                            time.sleep(1)
                            break
                    else:
                        for k in key_messages:
                            if k in if_title:
                                for ek in exclude_key_messages:
                                    if ek in if_title:
                                        break
                                else:
                                    custom_send_push(title, change_url(uri))
                                    print ">>Send_New|",
                                    time.sleep(1)
                                break
            else:
                for title, uri in result.iteritems():
                    custom_send_push(title, change_url(uri))
                    print ">>Send_Everything|",
                    time.sleep(1)
            result, my_hot_break_names = get_web_data_for_my_hot(
                new_list_request_raw, my_hot_break_names, web_data)
            for title, uri in result.iteritems():
                custom_send_push_my_hot(title, change_url(uri))
                print ">>Send_My_Hot|",
            print "Refresh|%s|" % datetime.datetime.now()

        time.sleep(random.randint(time_sleep, time_sleep+3))

        count += 1
        if count == WAIT_HOT_COUNT:
            result, hot_break_names = get_web_hot_data(hot_list_request_raw,
                                                       hot_break_names)
            count = 0
            if len(result) > MANY_HOT_TO_SEND_WITH_EMAIL_COUNT:
                email_msg = ""
                for title, uri in result.iteritems():
                    email_msg += email_msg_tmp.format(title, change_url(uri))
                tools.send_email(email_title, email_msg)
                print ">>Send_All_Hot-%s|" % len(result),
                continue
            for title, uri in result.iteritems():
                custom_send_push_hot(title, change_url(uri))
                print ">>Send_Hot|",
                time.sleep(1)
            print "Refresh_Hot|%s|" % datetime.datetime.now()
        sys.stdout.flush()
