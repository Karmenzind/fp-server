# -*- coding:utf-8 -*-

"""
    ping-pong
"""

from utils.routes import route
from utils import log as logger
from core.web import WebHandler


@route(r'/api/ping/$')
class Ping(WebHandler):

    async def get(self, *args, **kwargs):
        ret = {
            'ping': 'pong'
        }
        logger.debug('return ret:', ret, caller=self)
        self.do_success(ret)
