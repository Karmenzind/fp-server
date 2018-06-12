# -*- coding:utf-8 -*-

"""
FP-Server main settings
"""
# server's http port
HTTP_PORT = 12345

# redirect output to console other than log file
CONSOLE_OUTPUT = 1

# Log
LOG = {
    'level': 'debug',
    'dir': './logs',
    'filename': 'fpserver.log'
}

REDIS = {
    "host": '127.0.0.1',
    "port": 6379,
    "db": 0,
}

# stop crawling new proxies
# after stored enough proxied
PROXY_STORE_NUM = 500

# Check availability in cycle
PROXY_STORE_CHECK_SEC = 3600

