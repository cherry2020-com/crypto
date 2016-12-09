#!/usr/bin/env python
# coding=utf-8
"""

author = "minglei.weng@dianjoy.com"
created = "2016/12/7 0007"
"""
import asyncio
import logging
import pathlib

import aiohttp_jinja2
import jinja2
from aiohttp import web
import sqlalchemy as sa
import aiohttp_debugtoolbar
from aiohttp_debugtoolbar import toolbar_middleware_factory

from settings import PROJECT_ROOT
from utils import load_config
from db import init_db, close_db, create_db

from routes import setup_routes



def init():
    loop = asyncio.get_event_loop()
    # setup application and extensions
    app = web.Application(loop=loop, middlewares=[toolbar_middleware_factory])
    aiohttp_debugtoolbar.setup(app)
    conf = load_config(str(pathlib.Path(PROJECT_ROOT) / 'config' / 'polls.yaml'))
    app['config'] = conf
    create_db(app)
    # setup Jinja2 template renderer
    aiohttp_jinja2.setup(
        app, loader=jinja2.PackageLoader('step_by_step.demo_polls', 'templates'))
    # create connection to the database
    app.on_startup.append(init_db)
    # shutdown db connection on exit
    app.on_cleanup.append(close_db)
    # setup views and routes
    setup_routes(app)
    # setup_middlewares(app)

    return app

def main():
    # init logging
    logging.basicConfig(level=logging.DEBUG)

    app = init()
    web.run_app(app,
                host=app['config']['host'],
                port=app['config']['port'])

if __name__ == "__main__":
    main()