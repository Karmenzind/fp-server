# -*- coding:utf-8 -*-
# TODO: recon this ugly module

"""
Persistence utils

for `proxy` only
"""
import random
from itertools import chain

from scrapy import Item

from core.db.redis import aioredis_pool, pyredis_pool
from service.proxy.functions import (build_key, build_pattern,
                                     get_searchable_spec, key_prefix)
from service.proxy.serializers import ProxySerializer
from utils import log as logger

FAIL_TIMES_MAXIMUM = 5


class _ProxyServerBase:
    """
    common function
    """
    # TODO


class BlockingProxyServer(_ProxyServerBase):
    """
    pyredis version
    """

    def __init__(self):
        self.cli = pyredis_pool.acquire()
        self.cli.hmset_dict = self.hmset_dict

    def get_all_keys(self):
        return self.cli.keys('%s*' % key_prefix) or []

    def hgetall_dict(self, key):
        keys = self.cli.hkeys(key)
        vals = self.cli.hvals(key)

        return dict(zip(keys, vals))

    def hmset_dict(self, key, item):
        if not isinstance(item, (dict, Item)):
            raise TypeError("Error type: %s" % type(item))

        if not item:
            raise ValueError("item is empty")
        args = chain.from_iterable(item.items())

        return self.cli.hmset(key, *args)

    def delete(self, key, reason='Not specified.'):
        self.cli.delete(key)
        logger.info('Remove key: %s Reason: %s' % (key, reason))

    def add_failure(self, key):
        item = self.hgetall_dict(key)
        s = ProxySerializer(item)
        fail_times = int(item.get('fail_times', 0))
        current_fail_times = fail_times+1

        if current_fail_times >= FAIL_TIMES_MAXIMUM:
            self.delete(key, 'Failed %s times' % fail_times)
        else:
            if s.is_valid():
                self.cli.hincrby(key, 'fail_times', 1)
                logger.debug('Key: %s Fail times: %s' %
                             (key, current_fail_times))

    def save_proxy(self, item: dict):
        s = ProxySerializer(item)

        if s.is_valid(raise_e=True):
            save_res = self.cli.hmset_dict(s.key(), s.data())
            logger.debug(
                'Saving checked proxy: %s '
                'HMSET result: %s' % (item, save_res)
            )

    def query(self, spec, return_keys=False):
        result = []
        _spec = get_searchable_spec(spec)
        count = spec.get('count', 1)

        if count:
            keys = self.get_random_keys(count, _spec)

            if return_keys:
                result = keys
            else:
                for key in keys:
                    item = self.hgetall_dict(key)
                    result.append(item)

        return result

    def get_random_keys(self, count, spec=None):
        """
        :count: default 1
        :spec:  search conditions
        """
        keys = self.keys_by_dict(spec) or []

        if keys and len(keys) > count:
            keys = random.sample(keys, count)

        return keys

    def keys_by_dict(self, spec):
        _pattern = build_pattern(spec)
        keys = self.cli.keys(_pattern)

        return keys or []


class ProxyServer(_ProxyServerBase):
    """
    aioredis version
    """

    def __init__(self):
        self.cli = aioredis_pool

    async def get_all_status(self):
        all_keys = await self.get_all_keys()
        num = len(all_keys)
        http_keys = await self.keys_by_dict({"scheme": "http"})
        http_num = len(http_keys)
        https_num = num - http_num
        trans_keys = await self.keys_by_dict({"anonymity": "transparent"})
        trans_num = len(trans_keys)
        anony_num = num - trans_num
        ret = {
            "total": len(all_keys),
            "detail": {
                "http": http_num,
                "https": https_num,
                "transparent": trans_num,
                "anonymous": anony_num,
            }
        }

        return ret

    async def get_all_keys(self):
        return await self.cli.keys('%s*' % key_prefix) or []

    async def add_failure(self, key):
        item = await self.cli.hgetall(key)
        fail_times = int(item.get('fail_times', 0))
        s = ProxySerializer(item)

        current_fail_times = fail_times+1

        if current_fail_times >= FAIL_TIMES_MAXIMUM:
            await self.cli.delete(key)
            logger.info('Remove key: %s' % key)
        else:
            if s.is_valid():
                await self.cli.hincrby(key, 'fail_times', 1)
                logger.debug('Key: %s Fail times: %s' %
                             (key, current_fail_times))

    async def new_proxy(self, item):
        s = ProxySerializer(item)

        if s.is_valid(raise_e=True):
            save_res = await self.cli.hmset_dict(s.key, item)
            logger.info(
                'Got proxy: %s hmset result: %s' % (item, save_res)
            )

    async def query(self, spec, return_keys=False):
        result = []
        _spec = get_searchable_spec(spec)
        count = spec.get('count', 1)

        if count:
            keys = await self.get_random_keys(count, _spec)

            if return_keys:
                result = keys
            else:
                for key in keys:
                    item = await self.cli.hgetall(key)

                    result.append(item)

        return result

    async def get_random_keys(self, count, spec=None):
        """
        :count: default 1
        :spec:  search conditions
        """

        keys = await self.keys_by_dict(spec) or []

        if keys and len(keys) > count:
            keys = random.sample(keys, count)

        return keys

    async def keys_by_dict(self, spec):
        _pattern = build_pattern(spec)
        keys = await self.cli.keys(_pattern)

        return keys or []


proxy_srv = ProxyServer()
blocking_proxy_srv = BlockingProxyServer()

__all__ = [proxy_srv, blocking_proxy_srv]
