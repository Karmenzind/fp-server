# -*- coding:utf-8 -*-

"""
web基类
Date:   2017/8/8
Update: 2017/12/12  1. 增加do_prepare/do_complete函数;
        2017/12/17  1. 增加中间件;
        2017/12/18  1. 修改错误返回类型;
                    2. 增加 query_params 及 data 属性方法;
                    3. 删除 do_http_error 方法;
        2018/01/17  1. 跨域增加设置 Access-Control-Allow-Headers;
        2018/01/18  1. 返回datetime类型时间转换为UTC时间;
        2018/03/22  1. 修改__query_params为_query_params，__data为_data;
"""

import json
import datetime

from tornado.options import options
from tornado.web import RequestHandler

from tbag.core import exceptions
from tbag.utils import datetime_help


class WebHandler(RequestHandler):
    """ web基类
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
                    raise exceptions.ValidationError('请求的body是非json格式')
        return self._data

    def _to_representation(self, instance):
        """ 针对datetime类型数据做序列化
        """
        if isinstance(instance, datetime.datetime):
            return datetime_help.get_time_str(instance, datetime_help.UTC)
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
        """ 获取uri里边携带的参数
        * 直接调用 self.get_argument 如果不附加默认值，如果参数不存在，将会抛异常
        @param key 参数名
        @param defaut 默认如果参数不存在，就赋值None
        @return value 返回的参数值
        """
        value = self.get_argument(key, defaut)
        return value

    def get_params(self, *keys):
        """ 获取uri里边携带的参数
        @param keys 参数名列表
        @return values 返回的参数值列表
        """
        values = []
        for key in keys:
            value = self.get_param(key)
            values.append(value)
        return values

    def get_body(self, parse_json=True):
        """ 提取http请求的body数据
        @param parse_json 是否将body数据解析成json格式
        @return body http请求的body数据
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
        """ API成功返回
        """
        result = {
            'code': 0,
            'msg': msg,
            'data': self._to_representation(data)
        }
        self.do_finish(result)

    def do_failed(self, code=400, msg='error', data={}):
        """ API失败返回
        """
        result = {
            'code': code,
            'msg': msg,
            'data': self._to_representation(data)
        }
        self.set_status(200, 'OK')
        self.do_finish(result)

    def do_finish(self, result):
        """ 写入result
        """
        # 跨域
        cors = options.cors
        if cors:
            self.set_header('Access-Control-Allow-Origin', '*')
            self.set_header('Access-Control-Allow-Headers', '*')
        self.finish(result)

    def write_error(self, status_code, **kwargs):
        """ 这儿可以捕获自定义异常类
        * 此重写了父类函数
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
        """ 处理请求
        @param func_name 方法名 [_head_, _get_, _post_, _put_, _delete_, _patch_, _options_]
        @note 此处执行处理请求前的准备工作和处理请求完成的收尾工作
        """
        func = getattr(self, func_name, None)
        if not func:
            raise exceptions.NotFound()
        await self.do_prepare()
        await func(*args, **kwargs)
        await self.do_complete()

    async def do_prepare(self):
        """ 准备工作
        * 在执行http方法之前，可以做类似统计、权限校验等操作
        """
        # 中间件
        middlewares = options.middlewares
        for m in middlewares:
            await m.prepare(self)

    async def do_complete(self):
        """ 完成工作
        * 在执行http方法之后，可以做类似统计、日志记录等操作
        """
        # 中间件
        middlewares = options.middlewares
        for m in middlewares:
            await m.finish(self)
