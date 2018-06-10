#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for proxy
"""

import scrapydo
from tbag.utils import log as logger
from tbag.utils.routes import route
from service.proxy.proxy import proxy_srv

from proxy_spider.spiders.xicidaili import XicidailiSpider
from utils import exceptions
from utils.web import WebHandler

scrapydo.setup()


def return_developing():
    raise exceptions.NotFound(msg=exceptions.ERR_MSG_IS_DEVELOPING)


@route(r'/api/proxy/$')
class GetProxyHandler(WebHandler):
    """
    proxy api
    """

    async def get(self, *args, **kwargs):
        """
        get proxies
        """
        count = int(self.get_param('count', 1))
        scheme = self.get_param('scheme')
        anonymity = self.get_param('anonymity')
        spec = dict(count=count, scheme=scheme, anonymity=anonymity)
        items = await proxy_srv.query(spec)
        data = {
            "count": len(items),
            "detail": items,
        }
        # sort_by_speed = self.get_param('sort_by_speed', 0)

        self.do_success(data)

    async def post(self, *args, **kwargs):
        """ create proxies
        """
        datas = self.get_body()
        logger.debug('datas:', datas, caller=self)
        self.do_success({'ok': 1}, 'todo')

    async def delete(self, *args, **kwargs):
        """ delete proxies
        """
        self.do_success({'ok': 1}, 'todo')


@route(r'/api/proxy/report/$')
class ReposrProxyHandler(WebHandler):

    async def post(self, *args, **kwargs):
        self.do_success({'ok': 1}, 'developing..')


@route(r'/api/spider/$')
class TestSpiderHandler(WebHandler):

    async def get(self, *args, **kwargs):
        return_developing()
        scrapydo.run_spider(XicidailiSpider)
        self.do_success({'ok': 1}, 'todo')
