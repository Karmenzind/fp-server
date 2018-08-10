#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API for proxy
"""


from core import exceptions
from core.web import WebHandler
from service.proxy.proxy import proxy_srv
from service.proxy.serializers import ProxySerializer
from utils import log as logger
from utils.routes import route
from utils.tools import subdict


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

        if scheme:
            scheme = scheme.lower()

        anonymity = self.get_param('anonymity')
        spec = dict(count=count, scheme=scheme, anonymity=anonymity)
        _items = await proxy_srv.query(spec)
        items = []

        for i in _items:
            s = ProxySerializer(i)
            items.append(s.to_representation())

        data = {
            "count": len(items),
            "detail": items,
        }
        # sort_by_speed = self.get_param('sort_by_speed', 0)
        self.do_success(data)

    async def post(self, *args, **kwargs):
        """ create new proxies
        """
        item = self.get_body()
        indispensibles = ('scheme', 'ip', 'port')
        print(type(item), item)
        for k in indispensibles:
            if k not in item:
                raise exceptions.ValidationError('%s cannot be empty.' % k)

        _f = subdict(item, ['ip', 'port', 'scheme'])
        existed = await proxy_srv.keys_by_dict(_f)
        if existed:
            self.do_success({'success': 0, 'key': existed},
                            msg='key already existed')
            return

        try:
            _key = await proxy_srv.new_proxy(item)
            self.do_success({'success': 1, 'key': _key},
                            msg='created successfully')
            return
        except Exception as e:
            logger.exception('Failed: %s Detail: %s' % (item, e))
            self.do_failed(code=400, msg=str(e))

    async def delete(self, *args, **kwargs):
        """ delete proxies
        """
        self.do_success({'ok': 1}, 'todo')


@route(r'/api/proxy/report/$')
class ReportProxyHandler(WebHandler):

    async def post(self, *args, **kwargs):
        self.do_success({'ok': 1}, 'developing..')
