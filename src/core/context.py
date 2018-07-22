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
        """
        @param setting_module   the loaded setting module
            `DEBUG`             debug mode，default is False
            `CONSOLE_OUTPUT`    redirect log to console other than file if set to 1
            `LOG`               logging
                `level`         DEBUG/INFO/...
                `dir`           in which the log files be saved
                `filename`      log file's name
            `HANDLER_PATHES`    the uri handler module's relative path
            `HTTP_PORT`         HTTP port
            `MIDDLEWARES`       middlewares
            `ALLOW_CORS`        whether support CORS，default: false
            `COOKIE_SECRET`     cookie secret string
            `MYSQL`             mysql
            `MONGODB`           mongodb
            `REDIS`             redis
        """
        print(welcome)
        self.loop = None
        self.setting_module = setting_module

        self._install_twisted()
        self._init_event_loop_policy()
        self._get_event_loop()
        self._load_settings()
        self._init_logger()
        self._init_middlewares()
        self._init_crawler_runner()
        self._init_db_instance()
        self._init_uri_routes()
        self._init_application()
        self._db_initial_works()
        self._do_heartbeat()

    def start(self):
        """ start event loop
        """
        logger.info('start io loop ...')
        # self.loop.start()
        # self.loop.start()
        IOLoop.current().start()
        # self.loop.run_forever()

    def _init_event_loop_policy(self):
        asyncio.set_event_loop_policy(AnyThreadEventLoopPolicy())

    def _get_event_loop(self):
        # FIXIT
        # if not self.loop:
        #     # self.loop = IOLoop.current()
        #     # tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOMainLoop')
        #     self.loop = asyncio.get_event_loop()
        #     IOLoop().make_current()

        return self.loop

    def _load_settings(self):
        """ parse the settings
        """
        settings = __import__(self.setting_module, {}, {}, ['models'])

        # debug mode
        self.debug = getattr(settings, 'DEBUG', False)

        # whether open console_output
        self.console_output = getattr(settings, 'CONSOLE_OUTPUT', 1)

        # logging
        self.log_config = getattr(settings, 'LOG', {})

        # path for uri handlers
        self.handler_pathes = getattr(settings, 'HANDLER_PATHES', [])

        # server HTTP port
        if len(sys.argv) > 1:
            self.http_port = sys.argv[1]
        else:
            self.http_port = getattr(settings, 'HTTP_PORT', 10000)

        # middlewares
        self.middlewares = getattr(settings, 'MIDDLEWARES', [])

        # mysql
        self.mysql_config = getattr(settings, 'MYSQL', None)

        # mongodb
        self.mongo_config = getattr(settings, 'MONGODB', None)

        # redis
        self.redis_config = getattr(settings, 'REDIS', None)

        # support cors
        self.cors = getattr(settings, 'ALLOW_CORS', False)
        options.define(
            'cors',
            self.cors,
            help='set http response header `Access-Control-Allow-Origin` to `*`'
        )

        # cookie secret string
        self.cookie_secret = getattr(
            settings, 'COOKIE_SECRET', tools.get_uuid4())

    def _init_logger(self):
        """ create logger
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
        """ initialize uri routes
        """
        logger.info('init uri routes start >>>', caller=self)
        handlers = route.make_routes(self.handler_pathes)
        self.handlers = handlers
        logger.info('init uri routes done <<<', caller=self)

    def _init_db_instance(self):
        """ load database staff
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
        """ load middlewares
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
        from core.heartbeat import heartbeat, initial_tasks
        logger.info('Heartbeat started...')
        IOLoop.current().add_callback(heartbeat.start)
        IOLoop.current().add_callback(initial_tasks)

    def _init_crawler_runner(self):
        """ initialize scrapy env and crawler runner
        """
        from core.crawler import init_crawler_runner
        init_crawler_runner()

    def _db_initial_works(self):
        from core.db.initial_works import do_initial_works
        do_initial_works()

    def _install_twisted(self):
        import tornado.platform.twisted
        tornado.platform.twisted.install()
