#!/usr/bin/python
# -*- coding: UTF-8 -*-
from qiniu import Auth, put_file


def upload_attachment(path, local_path):
    access_key = 'XWpDUFV_Co1e99HOXwOAa3dhpbW-2mlFEt0uMm-O'
    secret_key = 'BAOE3piunVgmJKlBx44ADDv3unTfPGw6pd3AzzXO'
    q = Auth(access_key, secret_key)
    bucket_name = 'oneday'
    # 上传文件到七牛后， 七牛将文件名和文件大小回调给业务服务器。
    policy = {
        'callbackUrl': 'http://www.smallsite.cn/callback.php',
        'callbackBody': 'filename=$(fname)&filesize=$(fsize)'
    }
    token = q.upload_token(bucket_name, path, 3600, policy)
    ret, info = put_file(token, path, local_path)
    return u"http://{}/{}".format("www.smallsite.cn", path.strip('/'))
