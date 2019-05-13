#!/usr/bin/python
# -*- coding: UTF-8 -*-

# TODO gift 去掉title中已存在的
# TODO gitf 往后放
# TODO 进度


import json
import urlparse

import re
import collections

import sys

from utils import fiddler


GOOD_NAME_LIMIT = 50

DEBUG = True
DEBUG_PAGE_COUNT = 2
DEBUG_GOOD_IDS = ['100001674895', '100002258866', '100002258890']
DEBUG_GOOD_IDS = []


class JDParallel(object):

    def __init__(self, search_url, name_keyword=None, discount_keyword=None):
        self.search_url = search_url
        self.name_keyword = name_keyword
        self.discount_keyword = discount_keyword
        self.zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')

    def _get_coupon_batch(self):
        url_parse = urlparse.urlparse(self.search_url)
        url_param = dict([(k, v[0]) for k, v in urlparse.parse_qs(
            url_parse.query).items()])
        return url_param['coupon_batch']

    def _get_sample_string(self, string):
        string = string.replace(' ', '').replace('\n', '').replace('\r', '')
        while string.find('\\x') != -1:
            index = string.index('\\x')
            replace_str = string[index:index+4]
            string = string.replace(replace_str, '')
        return string

    def _get_web_goods(self, coupon_batch):
        web_all_goods = []
        fd = fiddler.RawToPython('./heads/goods_list.txt')
        fd.set_param(url_param={"coupon_batch": coupon_batch})
        page = 1
        while True:
            fd.set_param(url_param={'page': page})
            fd_data = fd.requests()
            fd_text = fd_data.text.strip()
            start_str = u'({'
            index = fd_text.find(start_str)
            if index != -1:
                fd_text = self._get_sample_string(fd_text)
                fd_text = u'{' + fd_text[index + len(start_str): -1]
                fd_json = json.loads(fd_text)
                web_all_goods.extend(fd_json['data']['searchm']['Paragraph'])
                good_count = fd_json['data']['searchm']['Head']['Summary']['ResultCount']
                page_count = fd_json['data']['searchm']['Head']['Summary']['Page']['PageCount']
                print '[v]Get Web Goods: Total-{}, Page-{}/{}'.format(good_count, page, page_count)
            else:
                raise Exception('Get Error Start String: {}'.format(fd_text[:len(start_str)]))
            if int(page_count) == page:
                break
            if DEBUG and DEBUG_PAGE_COUNT and DEBUG_PAGE_COUNT == page:
                break
            page += 1
        return web_all_goods

    def _get_format_goods(self, web_all_goods):
        all_goods = []
        for good in web_all_goods:
            all_goods.append({'name': good['Content']['warename'],
                              'pic': good['Content']['imageurl'],
                              'id': good['wareid']})
        return all_goods

    def _contain_zh(self, word):
        '''
        判断传入字符串是否包含中文
        :param word: 待判断字符串
        :return: True:包含中文  False:不包含中文
        '''
        word = word.decode()
        match = self.zh_pattern.search(word)
        return match

    def _get_all_discounts(self, all_goods):
        def try_name(each_info):
            for k, v in each_info.items():
                if k.isdigit():
                    end_flag = u"!@@!"
                    if end_flag not in v:
                        return 'discount', v
                    v = v.strip()
                    v_end_index = v.index(end_flag)
                    v_end = v[v_end_index+len(end_flag):]
                    v_start_json = json.loads(v[:v_end_index])
                    v_start = ''
                    for each in v_start_json:
                        v_start += u'【{1}】x {0}\n'.format(
                            each.get('nm', ''), each.get('num', ''))
                    else:
                        v_start = v_start.strip()
                    return 'gift', u'{}|{}'.format(v_end, v_start)
            # for k, v in each_info.items():
            #     if self._contain_zh(v):
            #         return v
            return None, None

        def get_info(fd_obj, url_temp, good):
            url = url_temp.format(good_id=good['id'])
            fd_text = fd_obj.requests(reset_url=url).text
            fd_text = self._get_sample_string(fd_text)
            start_str = u'window._itemInfo=('
            if start_str in fd_text:
                tmp_str = fd_text[fd_text.index(start_str) + len(start_str):]
                end_index = tmp_str.index(u');')
                json_text = tmp_str[:end_index]
                json_data = json.loads(json_text)
                # print json_data['promov2']['id']
                infos = reduce(lambda x, y: x + y,
                               [e['pis'] for e in json_data['promov2']])
                discounts = []
                for info in infos:
                    discount_type, name = try_name(info)
                    if not name:
                        continue
                    # TODO 你可以替换真正的ID，去找到真正的同一优惠
                    discounts.append({"name": name, 'id': name, 'type': discount_type})
                if discounts:
                    print u'[>]Find discount.\n   {}-{}\n'.format(
                        good['id'], good['name'][:GOOD_NAME_LIMIT])
                else:
                    print u'[>]Can not find discount.\n   {}-{}\n'.format(
                        good['id'], good['name'][:GOOD_NAME_LIMIT])
                return discounts
            else:
                raise Exception('Get Error Discount.')

        url_temp = '/product/{good_id}.html'
        fd_obj = fiddler.RawToPython('./heads/good_detail.txt')
        discounts_map = collections.defaultdict(list)
        all_discounts = {}
        goods_total_count = len(all_goods)
        for count, good in enumerate(all_goods, 1):
            good_url = 'https://item.m.jd.com/product/{}.html'.format(good['id'])
            print '[-]Request Url: {} - {}/{}'.format(good_url, count, goods_total_count)
            discounts = get_info(fd_obj, url_temp, good)
            if not discounts:
                continue
            all_discounts.update({x['id']: x for x in discounts})
            good_gifts = []
            for discount in discounts:
                if discount['type'] == 'gift':
                    good_gifts.append(discount)
            for discount in discounts:
                discounts_map[discount['id']].append({"good": good, "url": good_url,
                                                      'gifts': good_gifts})
        return discounts_map, all_discounts

    def _format_print(self, discounts_map, all_discounts):
        output_string = ''
        for id, infos in discounts_map.items():
            discount_type = all_discounts[id]['type']
            debug1 = ''
            if DEBUG:
                debug1 = u'[#]Discount Type: {}\n'.format(discount_type)
            part1 = u"╔{0} {1} {0}╗\n".format(
                u'═'*10, all_discounts[id]['name'][:GOOD_NAME_LIMIT])
            part2 = ''
            for info in infos:
                if discount_type == 'gift':
                    gifts = u'\n╞'.join(x['name'][:GOOD_NAME_LIMIT] for x in info['gifts']
                                        if x['name'] != all_discounts[id]['name'])
                else:
                    gifts = u'\n╞'.join(x['name'] for x in info['gifts'])
                tmp_part2 = u'-->{id}-{name}\n   {url}\n   {gifts}'.format(
                    id=info['good']['id'], name=info['good']['name'][:GOOD_NAME_LIMIT],
                    url=info['url'], gifts=(u'╞' + gifts) if gifts else '')
                part2 += tmp_part2.strip() + '\n'
            part3 = u"╚{0}═{1}═{0}╝\n".format(
                u'═'*10, u'═'*len(all_discounts[id]['name'][:GOOD_NAME_LIMIT]))
            main_string = debug1 + part1 + part2 + part3
            if discount_type == 'gift':
                output_string = output_string + main_string
            else:
                output_string = main_string + output_string
        print output_string

    def process(self):
        coupon_batch = self._get_coupon_batch()
        if DEBUG and DEBUG_GOOD_IDS:
            all_goods = [{'id': x, 'name': x, 'pic': x} for x in DEBUG_GOOD_IDS]
        else:
            web_all_goods = self._get_web_goods(coupon_batch)
            all_goods = self._get_format_goods(web_all_goods)
        discounts_map, all_discounts = self._get_all_discounts(all_goods)
        self._format_print(discounts_map, all_discounts)


if __name__ == '__main__':
    url = sys.argv[1]
    # url = 'https://wqsou.jd.com/coprsearch/cosearch?ptag=37070.3.2&showShop=1&coupon_batch=205740682&coupon_kind=1&coupon_shopid=0&coupon_aggregation=yes&coupon_p=undefined&coupon_v=undefined&coupon_t=138.0000&coupon_s=%E4%BB%85%E5%8F%AF%E8%B4%AD%E4%B9%B0%E4%B8%AA%E4%BA%BA%E6%8A%A4%E7%90%86%E9%83%A8%E5%88%86%E5%95%86%E5%93%81&coupon_d=undefined'
    JDParallel(url).process()
