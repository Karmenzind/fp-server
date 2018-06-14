# -*- coding:utf-8 -*-

import datetime
import json

from tornado.options import options
from tornado.web import RequestHandler

from utils import time_ext
from core import exceptions


class WebHandler(RequestHandler):
    """ web base handler
    """

    @property
    def query_params(self):
        if not hasattr(self, '_query_params'):
            self._query_params = {}

            for key in self.request.arguments.keys():
                value = self.get_argument(key)
                self._query_params[key] = value

        return self._query_params

    @property
    def data(self):
        if not hasattr(self, '_data'):
            self._data = None

            if self.request.body:
                try:
                    self._data = json.loads(self.request.body.decode('utf-8'))
                except:
                    raise exceptions.ValidationError('only support json')

        return self._data

    def _to_representation(self, instance):
        """ serialize datetime
        """

        if isinstance(instance, datetime.datetime):
            return time_ext.get_time_str(instance, time_ext.UTC)

        if isinstance(instance, datetime.date):
            return instance.isoformat()

        if isinstance(instance, list):
            return [self._to_representation(item) for item in instance]

        if isinstance(instance, dict):
            for key in instance.keys():
                instance[key] = self._to_representation(instance[key])

            return instance
        else:
            return instance

    def get_param(self, key, defaut=None):
        """ get param of request
        * avoid straightly raising exception while using self.get_argument
        @param key parameter's name
        @param defaut return None if key doesn't exist
        @return value value of param
        """
        value = self.get_argument(key, defaut)

        return value

    def get_params(self, *keys):
        """ get multiple params, see `get_param`
        @param keys list
        @return values list
        """
        values = []

        for key in keys:
            value = self.get_param(key)
            values.append(value)

        return values

    def get_body(self, parse_json=True):
        """ get body's data
        @param parse_json whether parse data with json
        @return body body's data
        """
        body = self.request.body

        if not body:
            return None

        if parse_json:
            try:
                body = json.loads(body.decode('utf8'))
            except:
                exceptions.ValidationError(msg='请求body数据格式错误')

        return body

    def do_success(self, data={}, msg='success'):
        """ for successful event
        """
        result = {
            'code': 0,
            'msg': msg,
            'data': self._to_representation(data)
        }
        self.do_finish(result)

    def do_failed(self, code=400, msg='error', data={}):
        """ for failed event
        """
        result = {
            'code': code,
            'msg': msg,
            'data': self._to_representation(data)
        }
        self.set_status(200, 'OK')
        self.do_finish(result)

    def do_finish(self, result):
        """ add tail work
        """
        # 跨域
        cors = options.cors

        if cors:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Headers', '*')
        self.finish(result)

    def write_error(self, status_code, **kwargs):
        """ custom exception
        * overwrote
        """
        exc_info = kwargs.get('exc_info')
        ex = exc_info[1]

        if isinstance(ex, exceptions.CustomException):
            self.do_failed(ex.code, ex.msg, ex.data)
        else:
            self.do_failed(500, '服务器内部错误')

    async def head(self, *args, **kwargs):
        await self.process('_head_', *args, **kwargs)

    async def get(self, *args, **kwargs):
        await self.process('_get_', *args, **kwargs)

    async def post(self, *args, **kwargs):
        await self.process('_post_', *args, **kwargs)

    async def put(self, *args, **kwargs):
        await self.process('_put_', *args, **kwargs)

    async def delete(self, *args, **kwargs):
        await self.process('_delete_', *args, **kwargs)

    async def patch(self, *args, **kwargs):
        await self.process('_patch_', *args, **kwargs)

    async def options(self, *args, **kwargs):
        await self.process('_options_', *args, **kwargs)

    async def process(self, func_name, *args, **kwargs):
        """ process the request
        @param func_name choices [_head_, _get_, _post_, _put_,
                                  _delete_, _patch_, _options_]
        @note preparation and finish work
        """
        func = getattr(self, func_name, None)

        if not func:
            raise exceptions.NotFound()
        await self.do_prepare()
        await func(*args, **kwargs)
        await self.do_complete()

    async def do_prepare(self):
        """ preparation
        * may add calculation or authentication here
        """
        middlewares = options.middlewares

        for m in middlewares:
            await m.prepare(self)

    async def do_complete(self):
        """ wind up
        * may add calculation or logging here
        """
        middlewares = options.middlewares

        for m in middlewares:
            await m.finish(self)
