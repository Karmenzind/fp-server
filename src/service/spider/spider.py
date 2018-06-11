# coding: utf-8

import time

import config
from initial import crawler_runner
from proxy_spider.spiders.checker import CheckerSpider
# from proxy_spider.spiders.ihuan import IhuanSpider
from proxy_spider.spiders.kuaidaili import KuaidailiSpider
from proxy_spider.spiders.xicidaili import XicidailiSpider
from proxy_spider.spiders.yundaili import YundailiSpider
from tbag.utils import log as logger
from utils.db import aioredis_pool, pyredis_pool
from utils.proxy import key_prefix as proxy_key_prefix
from utils.spider import build_key, key_prefix  # , updated_crawler_settings
# from scrapy.utils.log import configure_logging
from scrapy.crawler import Crawler
from tornado.ioloop import IOLoop
from tbag.core.db.redis import RedisDBBase


class SpiderServer:
    enabled_crawlers = {
        'crawler': (
            XicidailiSpider,
            KuaidailiSpider,
            YundailiSpider,
            # IhuanSpider,
        ),
        'checker': (
            CheckerSpider,
        )
    }
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
            st = await self.cli.get(k)

            if detail:
                total_time = None

                if st:
                    total_time = int(time.time()) - int(st)

                results.append({k: {
                    "start_time": st,
                    "total_time": total_time
                }})
            else:
                results.append(st)

        return results if keys else results[0]

    async def all_status(self):
        keys = await self.cli.keys('%s*' % key_prefix)
        if keys:
            return await self.check(keys=keys, detail=True)
        return []

    async def register_status(self, key):
        """

        :param key: will be deleted after crawling or last for some hours
        :param detail:
        :return:
        """
        t = int(time.time())

        await self.cli.set(key, t)
        await self.cli.expire(key, 4 * 3600)

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

    async def crawler_condition(self):
        keys = await self.cli.keys('%s*' % proxy_key_prefix) or []

        return len(keys) < config.PROXY_STORE_NUM

    async def start_crawling(self, _type='crawler'):
        """
        trigger spiders
        """

        started = []

        if _type == 'crawler' and not await self.crawler_condition():
            return

        for spider in self.enabled_crawlers[_type]:
            key = build_key(spider)
            running = bool(await self.check(key=key))

            if running:
                continue
            # register
            st = await self.register_status(key)
            # TODO: specify settings
            logger.info('Started %s at %s. Key: %s.' % (st, spider, key))
            self.run_crawler(spider, st, key)
            # IOLoop.current().run_in_executor(None, self.run_crawler, spider)
            started.append(key)

        return started

    def run_crawler(self, spider, st, key):
        crawler = self.get_crawler(spider)
        d = crawler_runner.crawl(crawler)
        # unregister
        d.addBoth(self.callback_unregister_status, st=st, key=key)

    def get_crawler(self, spider):
        """
        do some specific settings

        :param spider: spider class
        :return: crawler
        """
        settings = crawler_runner.settings

        # FIX it!
        # conf = {}
        # log_file = crawler_runner.settings.get('LOG_FILE')
        # if log_file:
        #     conf['LOG_FILE'] = '%s.%s' % (log_file, spider.name)
        #     conf['LOG_FILE'] = None
        #     conf['LOG_FORMAT'] = ('%(levelname)1.1s [%(asctime)s]'
        #                           ' [spider-{spider}]'
        #                           ' %(message)s'
        #                           ).format(spider=spider.name)
        #     settings = updated_crawler_settings(settings, conf)
        # configure_logging(settings)
        return Crawler(spider, settings)


spider_srv = SpiderServer()
__all__ = [spider_srv]
