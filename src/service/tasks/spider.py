# -*- coding:utf-8 -*-

from scrapy.crawler import Crawler
from tornado.ioloop import IOLoop

import config
from core.crawler import CRAWLER_RUNNER as crawler_runner
from core.crawler import spider_keymap
from service.proxy.proxy import proxy_srv
from service.spider.spider import spider_srv
from utils import log as logger


class SpiderTasks(object):
    """
    there are 2 kinds of spiders:
        seeker: to crawler new proxies
        checker: to check crawled proxies
    """

    async def start(self, *args, **kwargs):
        heart_beat_count = kwargs['heart_beat_count']

        def _checker_timers():
            # every 5 sec
            yield heart_beat_count < 60 and heart_beat_count % 5 == 0
            # every 1 min
            yield heart_beat_count >= 60 and heart_beat_count % 60 == 0

        def _crawler_timers():
            # every 10 sec
            yield heart_beat_count < 60 and heart_beat_count % 10 == 0
            # every 10 min
            yield heart_beat_count >= 60 and heart_beat_count % 600 == 0

        # consider using run_in_executor
        if any(_checker_timers()) and await self.checker_condition():
            IOLoop.current().add_callback(self.execute_task, 'checker')

        if any(_crawler_timers()) and await self.seeker_condition():
            IOLoop.current().add_callback(self.execute_task, 'seeker')

    async def execute_task(self, _type):
        key_and_spiders = await self.get_spiders_to_run(_type)

        return await self.start_crawling(key_and_spiders)

    async def checker_condition(self):
        """
        placeholder
        :return: bool
        """

        return True

    async def seeker_condition(self):
        """
        whether to start crawlers
        :return: bool
        """
        keys = await proxy_srv.get_all_keys()

        return len(keys) < config.PROXY_STORE_NUM

    def get_max_running_rum(self, _type):
        _map = getattr(config, 'MAX_RUNNING_NUM', {})
        max_num = _map.get(_type, 0)

        if max_num is None:
            max_num = 999999

        return max_num

    async def get_spiders_to_run(self, _type):
        """
        get spiders to run according to current status

        :param _type:
        :return: [(key, spider_cls)]
        """
        max_num = self.get_max_running_rum(_type)

        # all is turned off

        if not max_num:
            logger.info('No %s will run.' % _type)

            return []

        keymap = spider_keymap[_type]
        items = await spider_srv.all_status(_type=_type, with_key=True)

        alternatives = []

        # enough running spiders
        running_num = sum(1 for _ in items if _.get('status') == 'running')

        if (running_num >= max_num) or running_num >= len(keymap):
            logger.debug(
                'There are already %s running %ss.' % (running_num, _type)
            )

            return []

        # in keymap but not in redis
        existed_keys = [_['key'] for _ in items]

        if len(items) < len(keymap):
            alternatives += [k for k in keymap if k not in existed_keys]

        # not running
        not_running = [_ for _ in items if not (_.get('status') == 'running')]

        if not_running:
            sorted_spiders = sorted(
                not_running,
                key=lambda _: int(_.get('last_start_time', 0)),
            )
            alternatives += [_.get('key') for _ in sorted_spiders]

        if max_num:
            alternatives = alternatives[:max_num - running_num]
        return [(k, v) for k, v in keymap.items() if k in alternatives]

    async def start_crawling(self, key_and_spiders):
        """
        trigger spiders
        :param key_and_spiders: [(key, spider_cls)] spiders to run
        :return: [key]
        """
        deployed = []

        for key, spider in key_and_spiders:
            await self.deploy_spider(key, spider)
            deployed.append(key)

        return deployed

    async def deploy_spider(self, key, spider):
        """
        deploy a spider
        :param key:
        :param spider:
        :return:
        """
        # register
        st = await spider_srv.register_status(key)
        logger.info('Started %s at %s. Key: %s.' % (spider, st, key))

        # build a new thread
        # and run the crawler in it
        IOLoop.current().run_in_executor(None,
                                         self.run_spider,
                                         spider,
                                         st,
                                         key)

    def run_spider(self, spider, st, key):
        """ run a crawler, then unregister it
        * moved to another thread

        :st: start time
        :key: key in redis
        """
        crawler = self.build_crawler(spider)
        logger.info('Got crawler: %s' % crawler)
        d = crawler_runner.crawl(crawler)
        # unregister
        d.addBoth(spider_srv.callback_unregister_status, st=st, key=key)

    def build_crawler(self, spider):
        """
        do some specific settings for spider
        and return the wrapped crawler

        :param spider: spider class
        :return: crawler
        """
        # TODO: specify settings
        settings = crawler_runner.settings

        # FIXME !!!
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
