#coding=utf-8
import json
import requests
import io
import os
import urllib

#file = io.open('picture.json','r',encoding='utf-8')
#s = json.load(file)
#data = s['data']
#for img in data:
#    for each in img:
#        print each.get('Uri')
def save_url(get_url):
    web_data = requests.get(get_url)
    web_json = web_data.json()
    for each in web_json['data']:
#    print each['Title']
#        for uri in each['Images']:
        URI.append(each['Uri'])
    return URI

def save_img(img_url,file_name,file_path='./picture'):
    try:
        if not os.path.exists(file_path):
            print '文件夹',file_path,'不存在，重新建立'
            os.makedirs(file_path)
        file_suffix = os.path.splitext(img_url)[1]
        filename = '{}{}{}{}'.format(file_path,os.sep,file_name,file_suffix)
        urllib.urlretrieve(img_url,filename=filename)
    except IOError as e:
        print '文件操作失败',e
    except Exception as e:
        print '错误 ：',e

if __name__ == '__main__':
    URI = []
#    save_url('http://119.27.177.245/v1.2.2/tab/hot?p=1&size=20')
    save_url('http://119.27.177.245/v1.2.2/new?p=1&size=80')
    i = 0
    for img_url in URI:
        save_img(img_url,'biaoqing' + str(i))
        i = i +1





