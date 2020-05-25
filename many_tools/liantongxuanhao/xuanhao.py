#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import time
import requests
import json

from utils.fiddler import RawToPython
# url = 'https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_queryMoreNums&provinceCode=91&cityCode=940&monthFeeLimit=0&groupKey=19236028&searchCategory=3&net=01&amounts=200&codeTypeCode=&searchValue=&qryType=02&goodsNet=4&_='
# url = 'https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_queryMoreNums&provinceCode=91&cityCode=940&monthFeeLimit=0&groupKey=19236028&searchCategory=3&net=01&amounts=200&codeTypeCode=&searchValue=&qryType=02&goodsNet=4&_='
#https://card.10010.com/NumApp/NumberCenter/qryNum/token?callback=jsonp_queryMoreNums&provinceCode=91&cityCode=940&monthFeeLimit=0&searchCategory=3&net=01&amounts=200&codeTypeCode=&searchValue=&qryType=02&goodsNet=4&goodsId=911610241535&token=x7fHub9URZl8qRlMVBKkrte9If648jXM3B0XTu5mNOoMvtFP%2FQmhyoA%2FQh9CuGg9gFqCku4I4K8%2FdI%2B2PQm%2B6%2FE5ltRdm6xQjyUDDo1fcT65N4mQvOyOyVM4ZcIIivCbxiO%2F1tBeqoW6nYwCzIxfSVA8lUmel4QVYW5ciTMayU8%3D&channel=2I&_=1590065208436
url = 'https://m.10010.com/NumApp/NumberCenter/qryNum?callback=jsonp_queryMoreNums&provinceCode=11&cityCode=110&monthFeeLimit=0&groupKey=30242833&searchCategory=3&net=01&amounts=200&codeTypeCode=&searchValue=&qryType=02&goodsNet=4&_='
url = 'https://card.10010.com/NumApp/NumberCenter/qryNum/token?callback=jsonp_queryMoreNums&provinceCode=91&cityCode=940&monthFeeLimit=0&searchCategory=3&net=01&amounts=200&codeTypeCode=&searchValue=&qryType=02&goodsNet=4&goodsId=911610241535&token=x7fHub9URZl8qRlMVBKkrte9If648jXM3B0XTu5mNOoMvtFP%2FQmhyoA%2FQh9CuGg9gFqCku4I4K8%2FdI%2B2PQm%2B6%2FE5ltRdm6xQjyUDDo1fcT65N4mQvOyOyVM4ZcIIivCbxiO%2F1tBeqoW6nYwCzIxfSVA8lUmel4QVYW5ciTMayU8%3D&channel=2I&_='
start_num = 1522119232310
raw = RawToPython('./input/xuanhao.txt')
i = 0
all = set()
while i != 3000:
    i += 1
    start_num += 1
    try:
        web = requests.get(url + str(start_num), verify=False, timeout=5)
        web = web.text.strip().strip('jsonp_queryMoreNums(').strip(');')
        j = json.loads(web)['numArray']
        a = 0
        b = 0
        for x in j:
            if x not in [0, 1]:
                if x in all:
                    a += 1
                else:
                    b += 1
                    all.add(x)
        print 'in: {}, out: {}'.format(b, a),
    except:
         pass
    print i
    time.sleep(3)
with open('./output/xuanhao.txt', 'ab+') as f:
    for x in all:
        f.write(str(x) + '\n')
