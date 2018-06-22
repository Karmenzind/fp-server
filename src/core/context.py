# -*- coding:utf-8 -*-

import asyncio
import sys

from tornado import options
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AnyThreadEventLoopPolicy
from tornado.web import Application

from core.middleware import Middleware
from utils import log as logger
from utils import tools
from utils.routes import route

welcome = """
 _____ ____      ____
|  ___|  _ \    / ___|  ___ _ ____   _____ _ __
| |_  | |_) |___\___ \ / _ \ '__\ \ / / _ \ '__|
|  _| |  __/_____|__) |  __/ |   \ V /  __/ |
|_|   |_|       |____/ \___|_|    \_/ \___|_|

Github: https://github.com/Karmenzind/fp-server
E-Mail: valesail7@gmail.com
================================================
"""


class TornadoContext(object):

    def __init__(self, setting_module):
        """ 初始化
        @param setting_module   配置模块
            `DEBUG`             debug模式，默认为False
            `CONSOLE_OUTPUT`    redirect log to console other than file if set to 1
            `LOG`               日志配置
                `level`         级别 DEBUG/INFO
                `dir`           日志保存目录
                `filename`          日志名
            `HANDLER_PATHES`    uri注册处理器路径
            `HTTP_PORT`         HTTP监听端口号
            `MIDDLEWARES`       中间件配置
            `ALLOW_CORS`        是否支持跨域，True为支持，False为不支持，默认False
            `COOKIE_SECRET`     cookie加密字符串
            `MYSQL`             mysql配置
            `MONGODB`           mongodb配置
            `REDIS`             redis配置
        """
        print(welcome)
        self.loop = None
        self.setting_module = setting_module

        self._init_event_loop_policy()
        self._get_event_loop()
        self._load_settings()
        self._init_logger()
        self._init_middlewares()
        self._init_db_instance()
        self._init_crawler_runner()
        self._init_uri_routes()
        self._init_application()
        self._do_heartbeat()

    def _init_event_loop_policy(self):
        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

    def start(self):
        """ 启动
        """
        logger.info('start io loop ...')
        # self.loop.start()
        # self.loop.start()
        IOLoop.current().start()
        # self.loop.run_forever()

    def _get_event_loop(self):
        # if not self.loop:
        #     # self.loop = IOLoop.current()
        #     # tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOMainLoop')
        #     self.loop = asyncio.get_event_loop()
        #     IOLoop().make_current()

        return self.loop

    def _load_settings(self):
        """ 加载配置
        """
        settings = __import__(self.setting_module, {}, {}, ['models'])

        # 调试模式
        self.debug = getattr(settings, 'DEBUG', False)

        # 运行模式
        self.console_output = getattr(settings, 'CONSOLE_OUTPUT', 1)

        # 日志配置
        self.log_config = getattr(settings, 'LOG', {})

        # uri处理路径
        self.handler_pathes = getattr(settings, 'HANDLER_PATHES', [])

        # HTTP监听端口号

        if len(sys.argv) > 1:
            self.http_port = sys.argv[1]
        else:
            self.http_port = getattr(settings, 'HTTP_PORT', 10000)

        # 中间件
        self.middlewares = getattr(settings, 'MIDDLEWARES', [])

        # mysql配置
        self.mysql_config = getattr(settings, 'MYSQL', None)

        # mongodb配置
        self.mongo_config = getattr(settings, 'MONGODB', None)

        # redis配置
        self.redis_config = getattr(settings, 'REDIS', None)

        # 是否支持跨域
        self.cors = getattr(settings, 'ALLOW_CORS', False)
        options.define(
            'cors',
            self.cors,
            help='set http response header `Access-Control-Allow-Origin` to `*`'
        )

        # cookie加密字符串
        self.cookie_secret = getattr(
            settings, 'COOKIE_SECRET', tools.get_uuid4())

    def _init_logger(self):
        """ 初始化日志
        """
        level = self.log_config.get('level', 'debug')
        dirname = self.log_config.get('dir', './logs')
        filename = self.log_config.get('filename', 'fp-server.log')

        if self.console_output:
            logger.initLogger(level)
        else:
            log_filename = '%s_%s.log' % (
                filename.split('.')[0], self.http_port)
            logger.initLogger(level, dirname, log_filename)
        options.parse_command_line()

    def _init_uri_routes(self):
        """ 初始化uri路由
        """
        logger.info('init uri routes start >>>', caller=self)
        handlers = route.make_routes(self.handler_pathes)
        self.handlers = handlers
        logger.info('init uri routes done <<<', caller=self)

    def _init_db_instance(self):
        """ 初始化数据库对象
        """
        logger.info('init db instance start >>>', caller=self)

        if self.mysql_config:
            from core.db.mysql import initMySQL
            logger.info('mysql config:', self.mysql_config, caller=self)
            initMySQL(**self.mysql_config)

        if self.mongo_config:
            from core.db.mongo import initMongodb
            logger.info('mongodb config:', self.mongo_config, caller=self)
            initMongodb(**self.mongo_config)

        if self.redis_config:
            from core.db.redis import init_aioredis_pool
            logger.info('redis config:', self.redis_config, caller=self)
            # self.loop.run_until_complete(initRedisPool(**self.redis_config))
            # IOLoop.current().add_callback(initRedisPool, **self.redis_config)
            IOLoop.current().run_sync(init_aioredis_pool)
        logger.info('init db instance done <<<', caller=self)

    def _init_middlewares(self):
        """ 加载中间件
        """
        logger.info('load middleware start >>>', caller=self)
        middlewares = []

        for m in self.middlewares:
            l = m.split('.')
            class_name = l[-1]
            model = '.'.join(l[:-1])
            mo = __import__(model, {}, {}, ['classes'])
            middleware = getattr(mo, class_name)
            instance = middleware()

            if not isinstance(instance, Middleware):
                logger.warn(
                    'middleware must inherit from tbag.core.middleware.Middleware:', m, caller=self)

                continue
            middlewares.append(instance)
            logger.info('middleware:', middleware, caller=self)
        options.define('middlewares', middlewares,
                       help='set web api middlewares')
        logger.info('load middleware done <<<', caller=self)

    def _init_application(self):
        """ Initialize tornado app
        """
        settings = {
            'debug': self.debug,
            'cookie_secret': self.cookie_secret
        }
        app = Application(self.handlers, **settings)
        app.listen(self.http_port)
        logger.info('listen http port at:', self.http_port, caller=self)

    def _do_heartbeat(self):
        """ initialize heartbeat
        """
        from core.heartbeat import heartbeat
        logger.info('Heartbeat started...')
        IOLoop.current().add_callback(heartbeat.start)

    def _init_crawler_runner(self):
        """ initialize scrapy env and crawler runner
        """
        from core.crawler import init_crawler_runner
        init_crawler_runner()
