# -*- coding:utf-8 -*-

"""
fp-server
main entry
"""

import os
import sys

import tornado.httpserver
import tornado.platform.twisted
import tornado.web

from core.context import TornadoContext

# os.environ['PYTHONASYNCIODEBUG'] = '1'


def init_tasks():
    from core.heartbeat import heartbeat
    from service.tasks.spider import SpiderTasks
    spider_task = SpiderTasks()
    heartbeat.register(spider_task.start)


def main():
    """ launch
    """
    tornado.platform.twisted.install()
    TContext = TornadoContext(setting_module='config')
    init_tasks()
    TContext.start()


if __name__ == '__main__':
    src_dir = os.path.dirname(__file__)
    sys.path.insert(0, src_dir)
    main()
