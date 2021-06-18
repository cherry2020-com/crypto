# -*- coding: UTF-8 -*-
with open('./webdata.txt', 'rb') as f:
    file_data = f.readlines()
for each_line in file_data:
    each_line = each_line.strip()
    if not each_line:
        continue
    if each_line.startswith('#'):
        continue
    each_lines = [x for x in each_line.split('\t') if x]
    name = each_lines[-1].decode('utf-8')
    if name == u'联通':
        # print each_lines
        new_ip = '.'.join(each_lines[1].split('.')[:2] + ['0', '0'])
        print 'ufw allow from ' + new_ip + '/16'