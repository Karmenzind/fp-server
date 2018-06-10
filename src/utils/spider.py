# coding: utf-8
import config
import time
# corresponding key's prefix in redis while spider is running
key_prefix = 'spider_'


def get_specific_settings(spider_cls):
    result = {}
    if not config.CONSOLE_OUTPUT:
        from proxy_spider import settings
        filename = 'spider_%s.log' % spider_cls.name
        log_file = settings._get_log_path(filename)
        result['LOG_FILE'] = log_file

    return result


def build_key(spider_cls):
    """
    corresponding key in redis while spider
    is running
    """

    return '%s%s' % (key_prefix, spider_cls.name)


def need_check(last_check):
    interval = config.PROXY_STORE_CHECK_SEC
    now = int(time.time())
    return now - int(last_check) > int(interval)


def updated_crawler_settings(origin_settings, spec: dict):
    new_settings = origin_settings.copy()
    new_settings.setdict(spec)
    return new_settings

