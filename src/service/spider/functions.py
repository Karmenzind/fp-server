# coding: utf-8

# corresponding key's prefix in redis while spider is running
key_prefix = 'fp_server:spider:'
key_prefix_checker = '%schecker:' % key_prefix
key_prefix_seeker = '%sseeker:' % key_prefix


# import config
# def get_specific_settings(spider_cls):
#     result = {}
#
#     if not config.CONSOLE_OUTPUT:
#         from proxy_spider import settings
#         filename = 'spider_%s.log' % spider_cls.name
#         log_file = settings._get_log_path(filename)
#         result['LOG_FILE'] = log_file
#
#     return result


def prefix_by_type(_type=None):
    if _type:
        result = {
            'checker': key_prefix_checker,
            'seeker': key_prefix_seeker,
        }[_type]
    else:
        result = key_prefix
    return result


def build_key(spider_cls, _type):
    """
    corresponding key in redis while spider
    is running
    """
    _prefix = prefix_by_type(_type)
    return '%s%s' % (_prefix, spider_cls.name)


def updated_crawler_settings(origin_settings, spec: dict):
    new_settings = origin_settings.copy()
    new_settings.setdict(spec)

    return new_settings
