# -*- coding:utf-8 -*-

"""
服务器心跳

Date:   2017/05/08
Update: 2017/12/12  1、修改心跳日志打印为每5秒一次;
        2018/03/14  1. 修改模块名;
"""

import datetime

from tornado.ioloop import IOLoop

from utils import log as logger

__all__ = ('heartbeat',)


class HeartBeat(object):

    def __init__(self):
        self._count = 0
        self._interval = 1
        self.tasks = []

    def start(self):
        self._count += 1
        if self._count > 9999999:
            self._count = 1
        if self._count % 60 == 0:
            logger.info('Server heartbeat count:', self._count, caller=self)
        IOLoop.current().add_timeout(datetime.timedelta(seconds=self._interval), self.start)
        for task in self.tasks:
            func = task['func']
            args = task['args']
            kwargs = task['kwargs']
            kwargs['heart_beat_count'] = self._count
            IOLoop.current().add_callback(func, *args, **kwargs)

    def register(self, func, *args, **kwargs):
        """ register a task
        run it on each heartbeat
        @param func
        """
        t = {
            'func': func,
            'args': args,
            'kwargs': kwargs
        }
        self.tasks.append(t)


heartbeat = HeartBeat()
