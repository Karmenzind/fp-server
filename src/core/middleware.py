# -*- coding:utf-8 -*-

# TODO: change name to process_*


class Middleware:
    """ Base class of for middlewares
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
