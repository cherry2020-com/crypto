#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import json
import os
import sys

if len(sys.argv) > 4 or len(sys.argv) < 3:
    print(u'''请输入参数：
    参数1：需要追加配置（文件路径）；
    参数2：json文件（文件路径）；
    所有填写路径需要包括文件名！！！
    ''')
    raise Exception(u'请填写正确的参数')
if len(sys.argv) == 3:
    dest_src_path = sys.argv[2]
    add_src_path = sys.argv[1]
    output_dest_src_path = dest_src_path
else:
    dest_src_path = sys.argv[2]
    add_src_path = sys.argv[1]
    output_dest_src_path = sys.argv[3]

if not os.path.exists(add_src_path):
    raise Exception(u'需要追加配置的文件路径 不存在！')

exist_publishs = set()
dest_src = []
if os.path.exists(dest_src_path):
    with open(dest_src_path) as fr:
        try:
            dest_src = json.load(fr)
            exist_publishs = [y for y in dest_src]
            exist_publishs = [y[3] for y in exist_publishs]
            exist_publishs = set(exist_publishs)
        except ValueError:
            field_data = fr.read()
            field_data = field_data.strip()
            if field_data:
                raise Exception(u'原json 文件格式有误，请修改后再次运行！')

template = """
    [
        {},
        "{}",
        "{}",
        "{}"
    ]"""

need_adds = []
with open(add_src_path) as fr:
    each_add = {}
    for line in fr:
        line = line.strip()
        if not line:
            if each_add:
                need_adds.append(each_add)
            each_add = {}
            continue
        k, v = [x.strip() for x in line.split(':', 1) if x.strip()]
        each_add[k] = v
    else:
        if each_add:
            need_adds.append(each_add)

key_maps = {"hlsplay": 3, "rtmpplay": 1, "flvplay": 2}


add_strs = []

for each in dest_src:
    add_strs.append(template.format(*each))

for each in need_adds:
    for k, v in each.items():
        special_str = ''
        if k == 'publish':
            continue
        if k != 'rtmpplay':
            special_str = '/'
        main_line = each['publish'] + special_str + '%1'
        if main_line in exist_publishs:
            raise Exception(u'配置重复，请修改后再试！', main_line)
        each_add_str = template.format(key_maps[k],
                                       v + special_str + '.*',
                                       v + special_str + '(.*)',
                                       main_line)
        add_strs.append(each_add_str)
    exist_publishs.add(each['publish'] + '/' + '%1')
    exist_publishs.add(each['publish'] + '%1')

write_str = "[{}\n]".format(','.join(add_strs))
print(write_str)

with open(output_dest_src_path, 'w+') as fw:
    try:
        json.dumps(write_str)
    except ValueError:
        raise Exception(u'写入json时 json格式校验失败，可能程序出现问题！')
    fw.write(write_str)

print(u'任务完成！')
