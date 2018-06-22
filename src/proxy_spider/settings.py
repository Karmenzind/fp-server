# -*- coding: utf-8 -*-

# Scrapy settings for proxy_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os

import config

###################################################################
#                          do not change                          #
###################################################################

SPIDER_MODULES = ['proxy_spider.spiders']
NEWSPIDER_MODULE = 'proxy_spider.spiders'

BOT_NAME = 'proxy_spider'


def _get_log_config():
    """

    :return: file, level
    """
    _LEVEL = 'INFO'
    _FILE = None
    log_config = getattr(config, 'LOG', {})
    # fix: divide log from tornado log

    if not getattr(config, 'CONSOLE_OUTPUT', 0):
        dirname = log_config.get('dir', './logs')
        dirname = os.path.expanduser(dirname)

        if not os.path.exists(dirname):
            os.mkdir(dirname)

        _FILE = os.path.join(dirname, 'spider.log')
    main_level = log_config.get('level')

    if main_level:
        _LEVEL = main_level.upper()

    return _FILE, _LEVEL


# LOGGING
LOG_STDOUT = True
LOG_FILE, LOG_LEVEL = _get_log_config()

RETRY_TIMES = 10
RETRY_HTTP_CODES = [400, 500, 502, 503, 504, 408]

#######################################################################
#                               custom                                #
#######################################################################


# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'proxy_spider.middlewares.RandomUserAgentMiddleware': 543,
    'proxy_spider.middlewares.PureRedisMiddleware': 745,
    'proxy_spider.middlewares.TimerMiddleware': 746,
}

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 900
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'proxy_spider.pipelines.PersistencePipeline': 333,
}

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'h-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'proxy_spider.middlewares.ProxyspiderSpiderMiddleware': 543,
# }

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }
