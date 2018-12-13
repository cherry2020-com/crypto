# coding: utf-8
import requests
import time
import random
import json

# 填写你自己的cookies 类似
# citicbank=680c834a608c0975b24d0ba45f50; Path=/; JSESSIONID_BASEH5=2F030E589D2DBA291A12698370FF;Domain=.creditcard.ecitic.com;
# JSESSIONID_OAUTH=2F030E589D2AFA9DBA291A12690FF; citicbank_cookie=!Wf4ecja4M93O9AC7ZPLSyIDtKpLNBu7zgqHJZL7Pa0oC+J3V/kXEaqAScg+7mT3RPS7GmUb530; path=/;
Cookie = 'citicbank=43daf4bac9f0967b2190d2f42fb1a92e; Path=/; JSESSIONID_BASEH5=4397D66637648741455A1DF0FD3B7076; Domain=.creditcard.ecitic.com; JSESSIONID_OAUTH=4397D66637648741455A1DF0FD3B7076; citicbank_cookie=!GJtNYoZFkpVjJe67WDSPiZPLSyIDtF79aThznCwhK+ziW+eWdbjpJGPu90Mv/8g9/PZkAH1acILI3ss; path=/;'
# 下面就不要动啦


colors = ['blue', 'gold', 'green', 'black', 'red']  # 我自己三种刷子颜色啊，我不知道你们几种，自己加减吧。
headers = {'X-Requested-With': 'XMLHttpRequest',
          'Referer': 'https://servicewechat.com/wx13b9861d3e9fcdb0/10/page-frame.html',
          'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko)'
                        ' Mobile/16B93 MicroMessenger/6.7.4(0x1607041c) NetType/4G Language/zh_CN',
          'Accept': '*/*', 'Content-Type': 'application/json;charset=utf-8',
          'Cookie': Cookie}


def winterpig(type):
    residue = 1
    # 这里就是开始的。。。默认是有刷子的，人为的让它开始而已。。没实际意义
    while residue > 0:
        r = requests.post('https://s.creditcard.ecitic.com/citiccard/gwapi/uc/winterpig/pig/querycurrent', data='{}', headers=headers)
        if 'pigTypeName' not in r.text:
            print('请更新Cookies', r.text)
            break
        # print(r.text)
        pigTypeName = r.json()['data']['pig']['pigTypeName']
        residue = int(r.json()['data']['residue'])
        pigTypeId = r.json()['data']['pig']['pigTypeId']
        print(u'当前拥有刷子:{};;当前猪：{};;猪猪ID：{};;需要刷子：{};;'.format(residue, pigTypeName, r.json()['data']['pig']['id'] ,r.json()['data']['pig']['totalApply']))
        if residue >= 10:
            if type == 1:
                stepByStep(pigTypeId)
            else:
                onestepapply(pigTypeId)
        else:
            print('刷子数量不足')
            break

def reward():  # 查询奖品的
    r = requests.post('https://s.creditcard.ecitic.com/citiccard/gwapi/uc/winterpig/user/reward',data={},headers=headers)
    # print(r.text)
    if '000004' in r.text:
        print(r.json()['retMsg'])
    else:
        html = json.loads(r.text)
        for x in html['data']:
            print(x['rewardDate'], x['goodsName'])

def stepByStep(pigTypeId):
    if pigTypeId == 6:
        secs = ['face', 'body', 'earright', 'earleft', 'handright', 'handleft', 'nose', 'pants', 'footleft', 'footright']  # 十个部位一步步的涂。
    elif pigTypeId == 5:
        secs = ['face', 'body', 'earright', 'earleft', 'handright', 'handleft', 'nose', 'hair', 'footleft', 'footright']  # 十个部位一步步的涂。
    else:
        secs = ['face', 'body', 'nose', 'hand', 'foot']  # 十个部位一步步的涂。
    for sec in secs:
        color = colors[random.randint(0, len(colors)) - 1]
        print u'-->{}'.format(color)
        r = requests.post('https://s.creditcard.ecitic.com/citiccard/gwapi/uc/winterpig/pig/apply'
                          , data='{"userApply":{"sec":"%s","color":"%s"}}' % (sec, color), headers=headers)
        if 'goodsName' in r.text:
            print(u"{};;{};;{}".format(sec, r.json()['data']['lotteryData']['goodsName'],
                                      r.json()['data']['lotteryData']['goodsDesc']))
        else:
            print(u"{};;{}".format(sec, r.json()['retMsg']))
        time.sleep(3)

def onestepapply(pigTypeId):  # 一键涂猪
    color = colors[random.randint(0, len(colors)-1)]
    if pigTypeId == 6:
        data = '{"pigDetail":[{"sec":"face","color":"%s"},{"sec":"nose","color":"%s"},' \
               '{"sec":"earright","color":"%s"},{"sec":"earleft","color":"%s"},' \
               '{"sec":"body","color":"%s"},{"sec":"pants","color":"%s"},' \
               '{"sec":"handleft","color":"%s"},{"sec":"handright","color":"%s"},' \
               '{"sec":"footleft","color":"%s"},{"sec":"footright","color":"%s"}]' \
               '}' % (color,color,color,color,color,color,color,color,color,color)
    elif pigTypeId == 5:
        data = '{"pigDetail":[{"sec":"face","color":"%s"},{"sec":"nose","color":"%s"},' \
               '{"sec":"earright","color":"%s"},{"sec":"earleft","color":"%s"},' \
               '{"sec":"body","color":"%s"},{"sec":"hair","color":"%s"},' \
               '{"sec":"handleft","color":"%s"},{"sec":"handright","color":"%s"},' \
               '{"sec":"footleft","color":"%s"},{"sec":"footright","color":"%s"}]' \
               '}' % (color,color,color,color,color,color,color,color,color,color)
    else:
        data = '{"pigDetail":[{"sec":"face","color":"%s"},' \
               '{"sec":"nose","color":"%s"},' \
               '{"sec":"body","color":"%s"},' \
               '{"sec":"hand","color":"%s"},' \
               '{"sec":"foot","color":"%s"}]' \
               '}' % (color, color, color, color, color)
    r = requests.post('https://s.creditcard.ecitic.com/citiccard/gwapi/uc/winterpig/pig/onestepapply', data=data, headers=headers)
    print(r.text)
    time.sleep(3)

if __name__ == "__main__":
    type = input('输入命令：1、一笔一笔的涂。2、一键涂。3、查询当前账户下所有中奖纪录\n')
    if type != '3':
        winterpig(type)  # 一笔一笔的涂
    else:
        reward()

