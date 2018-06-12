# coding: utf-8

# These work had to be done here for now
# TODO: reconstruct

import os
import sys

# FIX: Why must crochet?
import crochet
crochet.setup()


def init_scrapy_env():
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    settings_dir = os.path.join(cur_dir, 'proxy_spider')
    # settings_mod = os.path.join(settings_dir, 'settings.py')
    sys.path.append(settings_dir)
    sys.path.append(cur_dir)

    os.environ['SCRAPY_PROJECT'] = 'proxy_spider'
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'proxy_spider.settings'


def init_crawler_runner():
    from scrapy.crawler import CrawlerRunner
    from scrapy.utils.project import get_project_settings

    settings = get_project_settings()

    return CrawlerRunner(settings)


init_scrapy_env()
crawler_runner = init_crawler_runner()

__all__ = [crawler_runner, ]
