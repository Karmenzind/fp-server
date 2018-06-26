# coding: utf-8

from utils import log as logger
from core.db.redis import pyredis_pool


def do_initial_works():
    """
    works after db initialized
    :return:
    """
    cli = pyredis_pool.acquire()

    from core.crawler import spider_keymap
    from service.spider.functions import key_prefix

    existed_keys = cli.keys('%s*' % key_prefix)

    for _type, _map in spider_keymap.items():
        for k, v in _map.items():
            if k in existed_keys:
                existed_keys.remove(k)
            cli.hmset(k,
                      'status', 'stopped',
                      'name', v.name)
    for k in existed_keys:
        cli.delete(k)
    logger.info('Finished database initial works.')
