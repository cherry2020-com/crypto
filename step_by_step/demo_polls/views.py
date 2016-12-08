#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/12/8 0008"
"""
import aiohttp_jinja2
from aiohttp import web

async def hello(request):
    # name = request.match_info.get('name', "Anonymous") # ???
    name = request.match_info["name"]
    reverse_url = request.app.router.named_resources()['hello'].url_for(
        name=name).with_query({"a": "b", "c": "d"})  # with_query("a=b&c=d")

    return web.Response(
        text="Hello [{}], world\n[{}]".format(name, reverse_url))

