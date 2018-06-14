# coding: utf-8

# These work had to be done here for now
# TODO: reconstruct

import os
import sys
from utils import log as logger

# XXX: Why must crochet?
import crochet
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings

CRAWLER_RUNNER = None


def init_scrapy_env():
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    settings_dir = os.path.join(cur_dir, 'proxy_spider')
    # settings_mod = os.path.join(settings_dir, 'settings.py')
    sys.path.append(settings_dir)
    sys.path.append(cur_dir)

    os.environ['SCRAPY_PROJECT'] = 'proxy_spider'
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'proxy_spider.settings'


def init_crawler_runner():
    crochet.setup()
    init_scrapy_env()
    settings = get_project_settings()
    global CRAWLER_RUNNER
    CRAWLER_RUNNER = CrawlerRunner(settings)
    logger.info('Initialized crawler runner: %s' % CRAWLER_RUNNER)


__all__ = [CRAWLER_RUNNER, ]
