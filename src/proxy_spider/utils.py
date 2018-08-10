# coding: utf-8


def build_proxy_url(ip, port, scheme,
                    user=None, password=None,
                    *args, **kw):
    need_auth = int(bool(user and password))
    auth_part = ''

    if need_auth:
        auth_part = '%s:%s@' % (user, password)

    result = '{scheme}://{auth}{ip}:{port}'.format(
        ip=ip,
        port=port,
        scheme=scheme,
        auth=auth_part,
    )

    return result
