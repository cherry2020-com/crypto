#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import hashlib
import socket
import sys

import binascii
import urlparse
from collections import OrderedDict

import crypto
import time
import base64
import urllib

sys.modules['Crypto'] = crypto
from Crypto.Cipher import AES


def get_auth_info(aes_key, ip, content_id, stb_id, timestamp=None):
    if not timestamp:
        timestamp = int(time.time())
    packed_ip_addr = socket.inet_aton(ip)
    hex_str = binascii.hexlify(packed_ip_addr)
    hex_ip = binascii.a2b_hex(hex_str)
    need_md5 = [stb_id, hex_ip, content_id, str(hex(timestamp)).replace('0x', '')]
    hl = hashlib.md5()
    hl.update('+'.join(need_md5))
    changed_md5 = hl.hexdigest()
    need_aes = need_md5 + [binascii.a2b_hex(changed_md5)]
    bs = AES.block_size
    pad = lambda s: s + (bs - len(s) % bs) * chr(bs - len(s) % bs)
    cipher = AES.new(aes_key)
    encrypted = cipher.encrypt(pad('+'.join(need_aes)))
    result = base64.b64encode(encrypted)
    result = urllib.quote(result, safe='')
    return result


if __name__ == '__main__':
    url = sys.argv[1]
    changed_url = urlparse.urlparse(url)
    changed_query = OrderedDict(urlparse.parse_qsl(changed_url.query))
    ip = sys.argv[2] if len(sys.argv) > 2 else '183.192.22.23'
    aes_key = sys.argv[3] if len(sys.argv) > 3 else "CMCCottsecurtkey"
    timestamp = int(sys.argv[4]) if len(sys.argv) > 4 else None
    content_id = changed_query['Contentid']
    stb_id = changed_query['stbId']
    auth_info = get_auth_info(aes_key, ip, content_id, stb_id, timestamp)
    changed_query['AuthInfo'] = auth_info
    re_changed_url = list(changed_url)
    re_changed_url[-2] = urllib.urlencode(changed_query)
    result_url = urlparse.urlunparse(re_changed_url)
    print ("url: " + result_url)
