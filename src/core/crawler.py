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

# from proxy_spider.spiders.ihuan import IhuanSpider
# from proxy_spider.spiders.ip89 import Ip89Spider
from proxy_spider.spiders.a3464 import A3464Spider
from proxy_spider.spiders.checker import CheckerSpider
from proxy_spider.spiders.coderbusy import CoderbusySpider
from proxy_spider.spiders.coolproxy import CoolproxySpider
from proxy_spider.spiders.data5u import Data5uSpider
from proxy_spider.spiders.ip66 import Ip66Spider
from proxy_spider.spiders.kuaidaili import KuaidailiSpider
from proxy_spider.spiders.mix import MixSpider
from proxy_spider.spiders.xicidaili import XicidailiSpider
from proxy_spider.spiders.yundaili import YundailiSpider

from service.spider.functions import build_key

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


# TODO: move these to config file?
enabled_spiders = {
    'seeker': (
        A3464Spider,
        CoderbusySpider,
        CoolproxySpider,
        Data5uSpider,
        Ip66Spider,
        KuaidailiSpider,
        MixSpider,
        XicidailiSpider,
        YundailiSpider,
        # Ip89Spider,
        # IhuanSpider,
    ),
    'checker': (
        CheckerSpider,
    )
}


def get_keymap():
    result = {}
    for _type, v in enabled_spiders.items():
        keymap = {}
        for spider_cls in v:
            key = build_key(spider_cls, _type)
            keymap[key] = spider_cls
        result[_type] = keymap
    logger.info("Got spiders' keymap: %s" % enabled_spiders)
    return result


spider_keymap = get_keymap()

__all__ = [CRAWLER_RUNNER, enabled_spiders]

if __name__ == '__main__':
    print(spider_keymap)
