# -*- coding:utf-8 -*-

import aioredis

from tbag.utils import log as logger

__all__ = ('initRedisPool', 'RedisDBBase')


REDIS_CONN_POOL = None  # redis连接池


async def initRedisPool(host='localhost', port=6379, db=None, *args, **kw):
    """ 初始化连接池
    """
    url = 'redis://%s:%s' % (host, port)
    global REDIS_CONN_POOL
    REDIS_CONN_POOL = await aioredis.create_redis_pool(url,
                                                       db=db,
                                                       encoding='utf-8')
    logger.info('Create redis pool success. Got pool: %s.' % REDIS_CONN_POOL)


class RedisDBBase:
    """ redis db基类
    """

    async def exec_cmd(self, *args, **kwargs):
        """ 执行命令
        """
        result = await REDIS_CONN_POOL.execute(*args, **kwargs)
        logger.debug('cmd:', *args, 'result:', result, caller=self)

        return result


#import asyncio
#from tornado.ioloop import IOLoop
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
