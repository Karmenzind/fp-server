# coding: utf-8
import re
import time

import config

key_prefix = 'proxy_'
IP_PATTERN = re.compile(r'^(\d+\.){3}\d+$')
PORT_PATTERN = re.compile(r'^\d+$')


def build_key(item):
    if not valid_format(item):
        raise AssertionError('Invalid item: %s' % item)

    key = '{prefix}{anonymity}:{scheme}:{ip}:{port}'.format(
        prefix=key_prefix,
        anonymity=item.get('anonymity'),
        scheme=item.get('scheme'),
        ip=item.get('ip'),
        port=item.get('port'),

    )

    return key


def build_pattern(spec):
    _pattern = '%s%s:%s:%s:%s' % (
        key_prefix,
        spec.get('anonymity') or '*',
        spec.get('scheme') or '*',
        spec.get('ip') or '*',
        spec.get('port') or '*',
    )

    return _pattern


def exceed_check_period(last_check):
    interval = config.PROXY_STORE_CHECK_SEC
    now = int(time.time())

    return now - int(last_check) > int(interval)


def valid_format(proxy_item):
    """
    check the format of ip and port

    :return: bool
    """
    scheme = proxy_item.get('scheme', '')
    ip = proxy_item.get('ip', '')
    port = proxy_item.get('port', '')

    def _conditions():
        yield scheme and ip and port
        yield scheme.lower() in ('http', 'https')
        yield IP_PATTERN.match(ip)
        yield PORT_PATTERN.match(port)

    return all(_conditions())
