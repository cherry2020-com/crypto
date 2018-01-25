#!/usr/bin/python
# - * - encoding: UTF-8 - * -
import argparse
import pdb
import threading

from collections import Iterable
from scapy.all import *
import scapy_http.http
# from scapy_ssl_tls.ssl_tls import *

from fiddler import RawToPython


def show(p, x=50):
    star = lambda x: '*' * x
    print star(x), '>>>', 'START', '<<<', star(x)
    if not isinstance(p, str) and isinstance(p, Iterable):
        print '\r\n'.join(p)
    else:
        print p + '\r\n'
    print star(x), '>>>', ' END ', '<<<', star(x)


def my_sniff(host, head, iface=None, filter=None, count=None):

    def _get_print(packet):
        p_data = packet.getlayer(scapy_http.http.HTTPRequest).fields
        # pdb.set_trace()  # 运行到这里会自动暂停
        if host and p_data.get('HOST', p_data.get('host', '')).lower() != host.lower():
            return
        # pdb.set_trace()  # 运行到这里会自动暂停
        h_k, h_v = [x.strip().lower() for x in head.split(':')]
        for k, v in p_data.items():
            if k.lower() == h_k and v.lower() == h_v:
                show(['{}: {}'.format(k, v) for k, v in p_data.items()])
                break
    try:
        sniff(lfilter=lambda x: x.haslayer(scapy_http.http.HTTPRequest), prn=_get_print,
              iface=iface, filter=filter, count=count, timeout=10)
    except:
        pass


def my_request(url):
    time.sleep(2)
    req = RawToPython('send_head.txt')
    web_data = req.requests(url=url)
    show(">>>web status code<<< : %s" % web_data.status_code)


if __name__ == '__main__':
    # Parser command line arguments and make them available.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Print HTTP Request headers (must be run as root or with capabilities to sniff).",
    )
    parser.add_argument("--interface", "-i", help="Which interface to sniff on.",
                        default=None)
    parser.add_argument("--filter", "-f", help='BPF formatted packet filter.',
                        default="tcp and port 80")
    parser.add_argument("--count", "-c",
                        help="Number of packets to capture. 0 is unlimited.", type=int,
                        default=0)
    parser.add_argument("--host", help="Http header HOST", default=None)
    parser.add_argument("--head", "-H", help="Http header", required=True)
    parser.add_argument("--url", "-U", help="Http URL", required=True)
    args = parser.parse_args()
    t1 = threading.Thread(target=my_sniff,
                          args=(args.host, args.head, args.interface, args.filter, args.count))
    t2 = threading.Thread(target=my_request, args=(args.url,))
    # t1.daemon = True
    # t2.daemon = True
    t1.start()
    t2.start()
    t1.join()
    t2.join()
