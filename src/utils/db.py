# coding: utf-8
from tbag.core.db.redis import REDIS_CONN_POOL

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

    return pool


# def init_aioredis_pool():
#     from tbag.core.db.redis import REDIS_CONN_POOL
#
#     pool = REDIS_CONN_POOL
#
#     return pool
# aioredis_pool = init_aioredis_pool()
# XXX: Why doesn't work?

aioredis_pool = REDIS_CONN_POOL

pyredis_pool = init_pyredis_pool()


def initial_clean():
    from utils.spider import key_prefix
    cli = pyredis_pool.acquire()

    for key in cli.keys('%s*' % key_prefix):
        cli.delete(key)


initial_clean()

__all__ = [pyredis_pool, aioredis_pool]
