# -*- coding:utf-8 -*-

import aioredis

from utils import log as logger

aioredis_pool = None


def get_redis_config():
    """parse redis config
    :returns: dict
    """
    import config
    redis_conf = getattr(config, 'REDIS', {})
    host = redis_conf.get('host', 'localhost')
    port = redis_conf.get('port', 6379)

    url = 'redis://%s:%s' % (host, port)  # FIXME
    result = dict(
        host=host,
        port=port,
        url=url,
        address=url,
        password=redis_conf.get('password') or None,
        db=redis_conf.get('db', 0),
        encoding=redis_conf.get('encoding', 'utf-8'),
        database=redis_conf.get('db', 0),
    )

    return result


redis_config = get_redis_config()


async def init_aioredis_pool():
    keys = ('address', 'db', 'password', 'encoding')
    conf = {k: v for k, v in redis_config.items() if k in keys}
    global aioredis_pool
    aioredis_pool = await aioredis.create_redis_pool(**conf)
    logger.info('Initialized aioredis pool: %s.' % aioredis_pool)


def init_pyredis_pool():
    from pyredis import Pool
    keys = ('host', 'port', 'database', 'password', 'encoding')
    conf = {k: v for k, v in redis_config.items() if k in keys}
    pool = Pool(**conf)
    logger.info('Initialized pyredis pool: %s' % pool)

    return pool


pyredis_pool = init_pyredis_pool()


def initial_clean():
    from service.spider.functions import key_prefix
    cli = pyredis_pool.acquire()

    to_delete = cli.keys('%s*' % key_prefix)

    for key in to_delete:
        cli.delete(key)
    logger.info('delete keys %s' % to_delete)


initial_clean()


class RedisDBBase:

    cli = aioredis_pool

    async def exec_cmd(self, *args, **kwargs):
        result = await aioredis_pool.execute(*args, **kwargs)
        logger.debug('cmd:', *args, 'result:', result, caller=self)

        return result


__all__ = (init_aioredis_pool, RedisDBBase, pyredis_pool, aioredis_pool)

#######################################################################
#                              snippits                               #
#######################################################################

# import asyncio
# from tornado.ioloop import IOLoop
#
# class RedisDBBase:
#     """ redis连接
#     """
#
#     def __init__(self, host='redis://127.0.0.1:6379', channel='test'):
#         self.pool = None    # 连接池
#         self.pub_conn = None    # publish连接
#         self.host = host
#         self.channel = channel
#
#     async def start(self):
#         await self._init_pool()
#         await self._init_publish()
#         await self._init_subscribe()
#
#     async def _init_pool(self):
#         """ 初始化连接池
#         """
#         self.pool = await aioredis.create_redis_pool(self.host, encoding='utf-8')
#         logger.info('create redis pool success.', caller=self)
#
#     async def _init_publish(self):
#         """ 初始化事件发布
#         """
#         self.pub_conn = await aioredis.create_redis(self.host)
#         logger.info('create redis publish channel success. channel:', self.channel, caller=self)
#
#     async def _init_subscribe(self):
#         """ 初始化订阅连接
#         """
#         sub = await aioredis.create_redis(self.host)
#         channel, = await sub.subscribe(self.channel)
#         await asyncio.ensure_future(self.async_reader(channel))
#         logger.info('subscribe channel success. channel:', self.channel, caller=self)
#
#     async def exec_redis_cmd(self, *args):
#         logger.debug('cmd:', *args, caller=self)
#         result = await self.pool.execute(*args)
#         return result
#
#     async def publish(self, content):
#         data = json.dumps(content)
#         await self.pub_conn.execute('PUBLISH', self.channel, data)
#         # logger.debug('content:', content, caller=self)
#
#     async def async_reader(self, channel):
#         while await channel.wait_message():
#             msg = await channel.get(encoding='utf-8')
#             data = json.loads(msg)
#             IOLoop.current().add_callback(WebsocketHandler.push_message, data)
#             # logger.debug('receive data:', data, caller=self)
#
#
# redis_srv = RedisDBBase()
# ioloop.run_until_complete(redis_srv.start())
#
