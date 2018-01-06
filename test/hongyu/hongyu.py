#!/usr/bin/python
# - * - encoding: UTF-8 - * -


def read_conf(fname):
    keys = ['server', 'if', 'location']
    result = {}
    active_key = ''
    with open(fname) as fr:
        for line in fr:
            line = line.strip().strip('{').strip('}')
            if not line:
                return
            line_split = line.split()
            if line_split[0] in keys:
                if line_split[0] == 'server':
                    active_key = line_split[0]
                else:
                    active_key = ' '.join(line_split)
                result.setdefault(active_key, [])
            else:
                result[active_key].append(line)
        print '-->', result


if __name__ == "__main__":
    print 'aaa'
    read_conf(u'前.txt')
