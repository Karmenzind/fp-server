# coding: utf-8
from copy import deepcopy

from core import exceptions
from proxy_spider.items import Proxy
from service.proxy import functions
from proxy_spider.utils import build_proxy_url


class ProxySerializer:
    """
    simple serializer
    """
    excluded = ['speed', 'last_check', 'fail_times']

    def __init__(self, item: dict):
        self._item = item

    def get_value(self, key):
        assert hasattr(self, '_is_valid'), (
            'You must call `.is_valid` at first'
        )
        return self._item.get(key)

    def is_valid(self, raise_e=False):
        """
        :param raise_e: whether raise exception
        :rtype: bool
        """
        self._is_valid = True

        validators = (
            self._validate_indispensibles,
            self._validate_type,
            self._validate_format,
        )

        try:
            for _v in validators:
                _v()
        except Exception as e:
            self._is_valid = False
            if raise_e:
                raise e
        return self._is_valid

    @property
    def data(self):
        return self._item

    @property
    def validated_data(self):
        assert hasattr(self, '_is_valid'), (
            'You must call `.is_valid` at first'
        )
        assert self._is_valid, 'Data is not valid.'
        result = dict(self._item)
        result['scheme'] = result['scheme'].lower()
        result.setdefault('url', build_proxy_url(**result))
        result.setdefault('last_check', 0)
        result.setdefault('fail_times', 0)
        result.setdefault('need_auth', 0)
        result.setdefault('anonymity', 'transparent')
        print(result)
        return result

    @property
    def key(self):
        """ key that used in redis """
        assert hasattr(self, '_is_valid'), (
            'You must call `.is_valid` at first'
        )
        assert self._is_valid, 'Invalid data.'
        return functions.build_key(self.validated_data)

    def to_representation(self):
        """
        only used in api
        """
        return {
            k: v for k, v in self._item.items()
            if k not in self.excluded
        }

    def _validate_indispensibles(self):
        indispensibles = ('scheme', 'ip', 'port')
        for k in indispensibles:
            if k not in self._item:
                raise exceptions.ValidationError('%s cannot be empty.' % k)

    def _validate_type(self):
        if not isinstance(self._item, Proxy):
            self._item = Proxy(self._item)

    def _validate_format(self):
        fmt_ok = functions.valid_format(self._item)
        assert fmt_ok, 'Format error %s' % self._item
