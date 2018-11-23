#!/usr/bin/python
# -*- coding: UTF-8 -*-
import io
import itchat
from itchat import config, utils
from itchat.components import contact
from itchat.returnvalues import ReturnValue


def new_get_head_img(self, userName=None, chatroomUserName=None, picDir=None):
    ''' get head image
     * if you want to get chatroom header: only set chatroomUserName
     * if you want to get friend header: only set userName
     * if you want to get chatroom member header: set both
    '''
    params = {
        'userName': userName or chatroomUserName or self.storageClass.userName,
        'skey': self.loginInfo['skey'],
        'type': 'big', }
    url = '%s/webwxgeticon' % self.loginInfo['url']
    if chatroomUserName is None:
        infoDict = self.storageClass.search_friends(userName=userName)
        if infoDict is None:
            return ReturnValue({'BaseResponse': {
                'ErrMsg': 'No friend found',
                'Ret': -1001, }})
    else:
        if userName is None:
            url = '%s/webwxgetheadimg' % self.loginInfo['url']
        else:
            chatroom = self.storageClass.search_chatrooms(userName=chatroomUserName)
            if chatroomUserName is None:
                return ReturnValue({'BaseResponse': {
                    'ErrMsg': 'No chatroom found',
                    'Ret': -1001, }})
            if 'EncryChatRoomId' in chatroom:
                params['chatroomid'] = chatroom['EncryChatRoomId']
            params['chatroomid'] =  params.get('chatroomid') or chatroom['UserName']
    headers = {'User-Agent': config.USER_AGENT }

    r = self.s.get(url, params=params, stream=True, headers=headers)
    print '-->', r.url
    tempStorage = io.BytesIO()
    for block in r.iter_content(1024):
        tempStorage.write(block)
    if picDir is None:
        return tempStorage.getvalue()
    with open(picDir, 'wb') as f:
        f.write(tempStorage.getvalue())
    tempStorage.seek(0)
    return ReturnValue({'BaseResponse': {
        'ErrMsg': 'Successfully downloaded',
        'Ret': 0, },
        'PostFix': utils.get_image_postfix(tempStorage.read(20)), })

# itchat.components.contact.get_head_img = new_get_head_img
itchat.get_head_img = new_get_head_img

import os

import PIL.Image as Image
from os import listdir
import math

itchat.auto_login(enableCmdQR=False, hotReload=True)

friends = itchat.get_friends(update=True)[0:]

user = friends[0]["UserName"]

print(user)

os.mkdir(user)

num = 0

for i in friends:
	img = itchat.get_head_img(itchat.originInstance, userName=i["UserName"])
	fileImage = open(user + "/" + str(num) + ".jpg",'wb')
	fileImage.write(img)
	fileImage.close()
	num += 1

pics = listdir(user)

numPic = len(pics)

print(numPic)

eachsize = int(math.sqrt(float(640 * 640) / numPic))

print(eachsize)

numline = int(640 / eachsize)

toImage = Image.new('RGBA', (640, 640))


print(numline)

x = 0
y = 0

for i in pics:
	try:
		#打开图片
		img = Image.open(user + "/" + i)
	except IOError:
		print("Error: 没有找到文件或读取文件失败")
	else:
		#缩小图片
		img = img.resize((eachsize, eachsize), Image.ANTIALIAS)
		#拼接图片
		toImage.paste(img, (x * eachsize, y * eachsize))
		x += 1
		if x == numline:
			x = 0
			y += 1


toImage.save(user + ".jpg")


itchat.send_image(user + ".jpg", 'filehelper')


