# coding: utf-8

import time

from core.db.redis import aioredis_pool, pyredis_pool
from service.spider.functions import prefix_by_type
from utils import log as logger


class SpiderServer:
    def __init__(self):
        self.cli = aioredis_pool
        self.blocking_cli = pyredis_pool.acquire()  # XXX: It's ugly

    async def all_status(self, _type=None, with_key=False):
        """
        get all status about spiders
        :param _type: spider's type
        :param with_key: whether return key in redis
        """
        key_prefix = prefix_by_type(_type)
        keys = await self.cli.keys('%s*' % key_prefix) or []

        result = []
        for key in keys:
            item = await self.cli.hgetall(key)
            if item['status'] == 'running':
                st = int(item.get('last_start_time'))
                item['total_time'] = int(time.time()) - st
            if with_key:
                item['key'] = key
            result.append(item)

        return result

    async def register_status(self, key):
        """

        :param key: will be deleted after crawling or last for some hours
        :param detail:
        :return:
        """
        t = int(time.time())

        spec = {
            'last_start_time': t,
            'status': 'running',
        }
        await self.cli.hmset_dict(key, spec)
        return t

    async def unregister_status(self, st, key, *args, **kw):
        """

        :param st: start time
        :param key: key in db
        :param args: preserved
        :param kw: preserved
        :return: preserved
        """
        st = await self.cli.hget(key, 'last_start_time')
        total_time = int(time.time()) - int(st)
        await self.cli.hset(key, "status", 'stopped')
        return total_time

    def callback_unregister_status(self, _, st, key, *args, **kw):
        """
        as callback of crawling
        * Twisted doesn't support aioredis

        :param _: preserved for fired deffer
        :param st: start time
        :param key: key in db
        :param args: preserved
        :param kw: preserved
        :return: preserved
        """
        total_time = int(time.time()) - int(st)
        logger.info("One spider finished working. "
                    "key: %s. Total time: %s"
                    % (key, total_time))

        return self.blocking_cli.hset(key, 'status', 'stopped'), total_time


spider_srv = SpiderServer()
__all__ = [spider_srv]
