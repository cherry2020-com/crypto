# coding: utf-8
# 创建一个session对象
a = u'63631939、63114623、63049082、62786254、62661142、62555779、62522523、62411319、62290502、62170264、62103025、61775845、61704422'
a_list = [int(x) for x in a.split(u'、')]
print a_list
l_x = 0
for x in a_list:
    print l_x - x
    l_x = x
