# coding: utf-8

key_prefix = 'proxy_'


def build_key(item):
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
