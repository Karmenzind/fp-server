# coding: utf-8
from service.proxy import functions


class ProxySerializer:
    """
    simple serializer
    """
    excluded = ['speed', 'last_check', 'fail_times']

    def __init__(self, item: dict):
        self._item = item

    def get_value(self, key):
        return self._item.get(key)

    def is_valid(self, raise_e=False):
        """
        :param raise_e: whether raise exception
        :rtype: bool
        """
        result = functions.valid_format(self._item)
        self._is_valid = result
        if not result and raise_e:
            raise AssertionError(
                'Format error %s' % self._item
            )
        return result

    def data(self):
        return dict(self._item)

    def key(self):
        if not hasattr(self, '_is_valid'):
            assert hasattr(self, '_is_valid'), (
                'You must call `.is_valid` at first'
            )
        return functions.build_key(self._item)

    def to_representation(self):
        """
        only used in api
        """
        return {
            k: v for k, v in self._item.items()

            if k not in self.excluded
        }
