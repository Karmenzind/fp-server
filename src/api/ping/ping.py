# -*- coding:utf-8 -*-

"""
    ping-pong
"""

from tbag.utils.routes import route
from tbag.utils import log as logger
from utils.web import WebHandler


@route(r'/api/ping/$')
class Ping(WebHandler):

    async def get(self, *args, **kwargs):
        ret = {
            'ping': 'pong'
        }
        logger.debug('return ret:', ret, caller=self)
        self.do_success(ret)
