# coding: utf-8
from utils import log as logger

proxy_key_prefix = 'proxy_'
spider_key_prefix = 'spider_'


def init_pyredis_pool():
    import config
    from pyredis import Pool
    redis_config = config.REDIS
    pool = Pool(
        host=redis_config.get('host', '127.0.0.1'),
        port=redis_config.get('port', 6379),
        encoding=redis_config.get('encoding', 'utf-8'),
        database=redis_config.get('db', 0),
    )
    logger.info('Initialized pyredis pool: %s' % pool)
    return pool


pyredis_pool = init_pyredis_pool()


def initial_clean():
    from utils.spider import key_prefix
    cli = pyredis_pool.acquire()

    for key in cli.keys('%s*' % key_prefix):
        cli.delete(key)


initial_clean()

__all__ = [pyredis_pool]  # , aioredis_pool]
