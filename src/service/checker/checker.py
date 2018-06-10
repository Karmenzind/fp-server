# -*- coding:utf-8 -*-

import time

import config
from initial import crawler_runner
from proxy_spider.spiders.checker import CheckerSpider
from tbag.utils import log as logger
from utils.db import aioredis_pool, pyredis_pool
from utils.spider import build_key, key_prefix

key_prefix = 'checker_'
key_expire_sec = 1200


class CheckerService:

    enabled_spiders = (
        CheckerSpider
    )
    cli = aioredis_pool
    blocking_cli = pyredis_pool.acquire()  # XXX: It's ugly

    async def check(self, key=None, keys=None, detail=False):
        """
        Argument:
            if detail:
                return detailed info
            else:
                return value(s)
        """

        if (key and keys) or (not key and not keys):
            raise AssertionError

        results = []
        _keys = keys or [key]

        for k in _keys:
            st = await self.cli.get(key)

            if detail:
                total_time = None

                if st:
                    total_time = int(time.time()) - int(st)

                results.append({
                    "is_running": bool(st),
                    "start_time": st,
                    "total_time": total_time
                })
            else:
                results.append(st)

        return results if keys else results[0]

    async def all_status(self):
        keys = await self.cli.keys('%s*' % self.key_prefix)

        return await self.check(keys=keys, detail=True)

    async def register_status(self, key):
        """

        :param key: will be deleted after crawling or last for some hours
        :param detail:
        :return:
        """
        t = int(time.time())

        await self.cli.set(key, t)
        await self.cli.expire(key, key_expire_sec)

        return t

    async def unregister_status(self, st, key, *args, **kw):
        """

        :param st: start time
        :param key: key in db
        :param args: preserved
        :param kw: preserved
        :return: preserved
        """
        st = await self.cli.get(key)
        total_time = int(time.time()) - int(st)

        return await self.cli.delete(key), total_time

    def callback_unregister_status(self, _, st, key, *args, **kw):
        """
        as callback of crawling
        Twisted doesn't support aioredis

        :param _: preserved for fired deffer
        :param st: start time
        :param key: key in db
        :param args: preserved
        :param kw: preserved
        :return: preserved
        """
        total_time = int(time.time()) - int(st)
        logger.info("One spider finished working. "
                    "Delete key: %s. Total time: %s"
                    % (key, total_time))

        return self.blocking_cli.delete(key), total_time

    async def start_crawling(self):
        """
        trigger spiders
        """

        started = []

        for spider in self.enabled_spiders:
            key = build_key(spider)
            running = bool(await self.check(key=key))

            if running:
                continue
            # register
            st = await self.register_status(key)
            started.append(key)
            # TODO: specify settings
            conf = {}

            if not config.CONSOLE_OUTPUT:
                conf['LOG_FILE'] = '%s%s.log' % (key_prefix, spider.name)

            logger.info('Started %s at %s. Key: %s.' % (st, spider, key))
            d = crawler_runner.crawl(spider)
            # unregister
            d.addBoth(self.callback_unregister_status, st=st, key=key)

        return started


checker_srv = CheckerService()
__all__ = [checker_srv]
