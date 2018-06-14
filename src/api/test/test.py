#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for proxy
"""

from utils.routes import route

from core.web import WebHandler


@route(r'/api/spider/run_all/$')
class TestSpiderHandler(WebHandler):

    async def get(self, *args, **kwargs):
        from service.spider.spider import spider_srv
        info = {
            'started': await spider_srv.start_crawling()
        }
        self.do_success(info, 'todo')
