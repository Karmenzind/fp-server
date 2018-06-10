# -*- coding:utf-8 -*-

"""
中间件 基类
Date:   2017/8/8
Update: None
"""


class Middleware:
    """ 中间件
    """

    async def prepare(self, request):
        """ 在HTTP请求的方法执行之前，执行此函数
        @param request HTTP请求实例
        """
        pass

    async def finish(self, response):
        """ 在HTTP请求返回成功之后，执行此函数
        @param response HTTP返回实例
        """
        pass
