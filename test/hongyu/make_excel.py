#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import datetime

import os
import pyexcel

EXCEL_PATH = u'/Users/mingleiweng/Downloads/d8ec379441785e9e.xls'
INDEX_KEYS = {u'省': 'province', u'运营商': 'operator', u'目标IP': 'target_ip',
              u'目标省份': 'target_province', u'目标运营商': 'target_operator',
              u'下载速度（B/s）': 'download_speed', u'建立连接总时间': 'connection_time'}
DOWNLOAD_SPEED_TEMPLATE = u'DOWNLOAD_SPEED:{province}-{operator}-{target_ip}-{download_speed:.2f}MB/S-{connection_time}ms'
CONNECTION_TIME_TEMPLATE = u'CONNECTION_TIME:{province}-{operator}-{target_ip}-{download_speed:.2f}MB/S-{connection_time}ms'
TITLE_LINE_INDEX = 2


def get_index_map(sheet_data):
    first_row = sheet_data[TITLE_LINE_INDEX]
    index_map = {}
    for index, value in enumerate(first_row):
        if value in INDEX_KEYS:
            if value in index_map:
                raise Exception('Repeated key, index: %s.' % index)
            index_map[INDEX_KEYS[value]] = index
    if len(index_map) != len(INDEX_KEYS):
        raise Exception('Not enough keys')
    return index_map


def get_valid_data(sheet_data, index_map):
    valid_data = []
    for row in sheet_data[TITLE_LINE_INDEX + 1:]:
        if (row[index_map['province']] == row[index_map['target_province']] and
                row[index_map['operator']] == row[index_map['target_operator']]):
            valid_data.append(row)
    return valid_data


def make_data(valid_data, index_map):
    level_5_download_speed = 2.9
    level_5_connection_time = 42
    download_speed_result = []
    connection_time_result = []
    all_result = []
    make_keys = set()
    for row in valid_data:
        download_speed = int(str(row[index_map['download_speed']]))
        connection_time = float(str(row[index_map['connection_time']]))
        is_append = False
        is_error = False
        if download_speed <= level_5_download_speed * 1024 * 1024:
            download_speed_result.append(row)
            is_append = True
            all_result.append(row)
            is_error = True
        if connection_time * 1000 >= level_5_connection_time:
            if not is_append:
                all_result.append(row)
            connection_time_result.append(row)
            is_error = True
        if not is_error:
            make_keys.add((row[index_map['province']],
                           row[index_map['operator']],
                           row[index_map['target_ip']]))

    def remove_data(error_rows):
        new_result_rows = []
        for error_row in error_rows:
            make_key = (error_row[index_map['province']],
                        error_row[index_map['operator']],
                        error_row[index_map['target_ip']])
            if make_key not in make_keys:
                new_result_rows.append(error_row)
        return new_result_rows

    download_speed_result = remove_data(download_speed_result)
    connection_time_result = remove_data(connection_time_result)
    all_result = remove_data(all_result)

    def list_sort(elem):
        return "%s-%s-%s" % (elem[index_map['province']], elem[index_map['operator']],
                             elem[index_map['target_ip']])
    download_speed_result.sort(key=list_sort)
    connection_time_result.sort(key=list_sort)
    all_result.sort(key=list_sort)
    return download_speed_result, connection_time_result, all_result


def formatted_output(result_rows, index_map):
    download_speed_result, connection_time_result, _ = result_rows
    download_speed_result_len = len(download_speed_result)
    all_rows = download_speed_result + connection_time_result
    row_dict = {}
    for row_index, row in enumerate(all_rows):
        for index_value in INDEX_KEYS.values():
            row_data = row[index_map[index_value]]
            if index_value == 'download_speed':
                row_data = int(str(row_data)) / 1024.0 / 1024.0
            elif index_value == 'connection_time':
                row_data = int(float(str(row_data)) * 1000)
            row_dict[index_value] = row_data
        if row_index < download_speed_result_len:
            print(DOWNLOAD_SPEED_TEMPLATE.format(**row_dict))
        else:
            print(CONNECTION_TIME_TEMPLATE.format(**row_dict))


def save_result(result_rows):
    _, _, all_result = result_rows
    if not all_result:
        return
    result_file_name = u"Less_than_level_5_%s.xlsx" % datetime.datetime.now()
    result_file_path = os.path.join(os.path.dirname(EXCEL_PATH), result_file_name)
    pyexcel.save_as(dest_file_name=result_file_path,
                    array=(sheet_data[:TITLE_LINE_INDEX + 1] + all_result))


if __name__ == '__main__':
    excel_data = pyexcel.get_book_dict(file_name=EXCEL_PATH)
    sheet_data = excel_data.values()[0]

    index_map = get_index_map(sheet_data)
    valid_data = get_valid_data(sheet_data, index_map)
    result_rows = make_data(valid_data, index_map)
    formatted_output(result_rows, index_map)
    save_result(result_rows)
