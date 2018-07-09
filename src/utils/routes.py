# -*- coding:utf-8 -*-

"""
http uri 路由装饰器
"""

from utils import log as logger


class route(object):
    """
    @route('/some/path')
    class SomeRequestHandler(RequestHandler):
        pass
    @route('/some/path', name='other')
    class SomeOtherRequestHandler(RequestHandler):
        pass
    my_routes = route.make_routes(['api'])
    """

    _routes = []

    def __init__(self, uri, name=None):
        """ 装饰器
        @param uri 注册的uri名字，支持uri正则表达式
        @param name 注册的uri别名
        """
        self.uri = uri

        if not name:
            name = '-'.join(uri.split('/'))
        self.name = name

    def __call__(self, _handler):
        """ gets called when we class decorate
        """

        for item in self._routes:
            if item.get('uri') == self.uri:
                logger.error('uri aleady exists! uri:', self.uri,
                             'name:', self.name, 'handler:', _handler,
                             caller=self)

            if item.get('name') == self.name:
                logger.warn('name aleady exists! uri:', self.uri,
                            'name:', self.name, 'handler:', _handler,
                            caller=self)
        self._routes.append({'uri': self.uri, 'name': self.name,
                             'handler': _handler})

        return _handler

    @classmethod
    def make_routes(cls, dirs):
        """ 注册并返回所有的handler
        @param dirs list，需要注册uri路由的处理方法路径
        """

        for dir in dirs:
            s = 'import %s' % dir
            exec(s)
        routes = []

        for handler_dic in cls._routes:
            logger.info('register uri:', handler_dic['uri'],
                        'handler:', handler_dic.get('handler'),
                        caller=cls)
            routes.append(
                (handler_dic.get('uri'), handler_dic.get('handler'))
            )

        return routes
