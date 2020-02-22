#!/usr/bin/python
# -*- coding: UTF-8 -*-
import collections
import sys


class BuyBuyBuy(object):
    def __init__(self, input_str, input_count_str=None):
        self.input_str = input_str
        input_count_str = input_count_str or ''
        self.input_count_str = input_count_str.strip()
        self.input_count, self.use_input_unit = self.get_input_count(input_count_str)
        self.my_name = u'李翀'

    def get_input_count(self, input_count_str):
        input_count = self.get_row_order_number(input_count_str)
        if not input_count:
            input_count = None
        use_input_unit = None
        if not self.input_count_str.isdigit():
            use_input_unit = self.input_count_str
            input_count = None
        return input_count, use_input_unit

    def get_clean_rows(self):
        input_str = self.input_str.strip()
        clean_rows = []
        input_list = input_str.split('\n')
        for each in input_list:
            each = each.strip()
            if each:
                clean_rows.append(each)
        return clean_rows

    def get_row_order_number(self, row):
        num = ''
        for each in row:
            if each.isdigit():
                num += each
            else:
                break
        if num:
            return int(num)
        return None

    def is_valid(self, clean_rows):
        last_row = clean_rows[-1]
        last_order = self.get_row_order_number(last_row)
        if len(clean_rows) >= 2:
            last_2_row = clean_rows[-2]
            last_2_order = self.get_row_order_number(last_2_row)
            if not last_2_order:
                if last_order:
                    return True
                else:
                    return False
            else:
                if last_order:
                    if (last_2_order + 3) < last_order:
                        return False  # 如果最后一行的数比倒数第二行的数+3还大就很有可能是管理员在数人数而放在最后一行。
                    else:
                        return True
                else:
                    return False
        else:
            return True  # 就一行数据就说明可能是刚刚开始的团

    def only_number_row(self, row, split_symbols):
        order_number = self.get_row_order_number(row)
        if order_number is None:
            return False
        if row == self.to_unicode(order_number):
            return True
        for _symbol in (split_symbols + [u' ']):
            if row == u'{}{}'.format(order_number, _symbol):
                return True
        return False

    def get_way(self, clean_rows, all_split_symbols):
        for row in clean_rows:
            if self.only_number_row(row, all_split_symbols):
                way = 'order_number_exists'
                break
        else:
            way = 'no_order_number'
        return way

    def get_my_row_str(self, order, split_symbol, unit):
        result = u'{order}{split_symbol}{my_name}'.format(
            order=order, split_symbol=split_symbol, my_name=self.my_name)
        if self.input_count:
            result += u' {input_count}{unit}'.format(input_count=self.input_count,
                                                     unit=unit)
        if self.use_input_unit:
            result += u' {}'.format(self.use_input_unit)
        return result

    def to_unicode(self, src):
        if not isinstance(src, basestring):
            src = str(src)
        return src.decode('utf-8')

    def to_utf8(self, src):
        return src.encode('utf-8')

    def get_split_symbol(self, clean_rows):
        split_symbols = []
        for index, row in enumerate(clean_rows):
            order_number = self.get_row_order_number(row)
            if order_number is None:
                continue
            if self.to_unicode(order_number) == row:
                split_symbols.append(' ')
                continue
            split_symbols.append(row[len(str(order_number))])
        split_symbols_count_map = {}
        if split_symbols:
            split_symbols_count_map = collections.Counter(split_symbols)
        max_count = 0
        good_split_symbol = u' '
        all_split_symbols = []
        for _symbol, _count in split_symbols_count_map.iteritems():
            all_split_symbols.append(_symbol)
            if _count > max_count:
                good_split_symbol = _symbol
                max_count = _count
        if max_count and max_count <= 2:
            good_split_symbol = u' '
        return good_split_symbol, all_split_symbols

    def get__no_order_number(self, clean_rows, split_symbol, all_split_symbols, good_unit):
        last_row = clean_rows[-1]
        order_number = self.get_row_order_number(last_row)
        my_row = self.get_my_row_str(order_number+1, split_symbol, good_unit)
        return u'\n'.join(clean_rows + [my_row])

    def get__order_number_exists(self, clean_rows, split_symbol, all_split_symbols, good_unit):
        results = []
        my_row_str = None
        for row in clean_rows:
            order = self.get_row_order_number(row)
            if not my_row_str and order and self.only_number_row(row, all_split_symbols):
                # 获得到 填写位置
                my_row_str = self.get_my_row_str(order, split_symbol, good_unit)
                results.append(my_row_str)
            else:
                results.append(row)
        return u'\n'.join(results)

    def get_unit(self, clean_rows):
        if not self.input_count:
            return ''
        unit_list = []
        for row in clean_rows:
            order_number = self.get_row_order_number(row)
            if order_number is not None:
                unit_list.append(row[-1])
        unit_list_count_map = {}
        if unit_list:
            unit_list_count_map = collections.Counter(unit_list)
        max_count = None
        good_unit = ''
        for _unit, _count in unit_list_count_map.iteritems():
            if _count > max_count:
                good_unit = _unit
                max_count = _count
        if max_count and max_count <= 2:
            good_unit = ''
        if not good_unit and self.input_count > 1:
            good_unit = u'份'
        if good_unit.isdigit():
            good_unit = ''
        return good_unit

    def is_exist_me(self):
        if self.my_name in self.input_str:
            return True
        return False

    def start(self):
        clean_rows = self.get_clean_rows()
        error_msg = u''
        if not self.is_valid(clean_rows):
            error_msg += u"复制错误或该团已经结束，请检查！"
        elif self.is_exist_me():
            error_msg += u"剪切板已经包含「{my_name}」，请检查!".format(my_name=self.my_name)
        if error_msg:
            error_msg += u"\n\n如果剪切板内容想保留请点击下方\"取消\"按钮"
            return self.to_utf8(error_msg)
        good_split_symbol, all_split_symbols = self.get_split_symbol(clean_rows)
        good_unit = self.get_unit(clean_rows)
        way = self.get_way(clean_rows, all_split_symbols)
        result = getattr(self, 'get__{}'.format(way))(clean_rows, good_split_symbol,
                                                      all_split_symbols, good_unit)
        return self.to_utf8(result)


if __name__ == '__main__':
    # test_str = u"""我们买东西啦！！！！
    # 1.qwe
    # 2
    # 3
    # 4
    # 5
    # 6
    # 7
    # 8:
    # 9:
    # 10:"""
    # test_str = u"""我们买东西啦！！！！
    #     1.qwe
    #     2： 你好啊
    #     3： 我是说
    #     4： 不好说
    #     """
    with open('/home/minglei/tmp.txt') as f:
        _input_string = f.read()
    # _input_string = sys.argv[1].decode('utf-8')
    _input_count = sys.argv[1]
    try:
        _input_string = _input_string.decode('utf-8')
        _input_count = _input_count.decode('utf-8')
        print BuyBuyBuy(_input_string, _input_count).start()
    except Exception as e:
        print str(e)
        raise
