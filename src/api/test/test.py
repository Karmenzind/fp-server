#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for proxy
"""

from tbag.utils import log as logger
from tbag.utils.routes import route

from utils import exceptions
from utils.web import WebHandler


@route(r'/api/spider/run_all/$')
class TestSpiderHandler(WebHandler):

    async def get(self, *args, **kwargs):
        from service.spider.spider import spider_srv
        info = {
            'started': await spider_srv.start_crawling()
        }
        self.do_success(info, 'todo')
