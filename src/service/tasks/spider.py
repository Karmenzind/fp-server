# -*- coding:utf-8 -*-

from tornado.ioloop import IOLoop

from service.spider.spider import spider_srv


class SpiderTasks(object):

    async def start(self, *args, **kwargs):
        heart_beat_count = kwargs['heart_beat_count']

        def _checker_conditions():
            yield heart_beat_count < 60 and heart_beat_count % 10 == 0
            # every 1 min
            yield heart_beat_count > 60 and heart_beat_count % 60 == 0

        def _crawler_conditions():
            yield heart_beat_count < 60 and heart_beat_count % 10 == 0
            # every 10 min
            yield heart_beat_count > 60 and heart_beat_count % 600 == 0

        # IOLoop.current().run_in_executer()
        if any(_checker_conditions()):
            IOLoop.current().call_later(1, self.execute_task, 'checker')

        if any(_crawler_conditions()):
            IOLoop.current().call_later(1, self.execute_task, 'crawler')

    async def execute_task(self, _type):
        return await spider_srv.start_crawling(_type)
