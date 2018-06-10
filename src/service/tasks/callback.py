# -*- coding:utf-8 -*-

"""
    回调任务
"""

from tbag.utils import tools
from tbag.utils import log as logger
from tornado.ioloop import IOLoop
from tbag.utils.http_client import AsyncHttpRequests

from service.callback.callback import callback_srv


class CallbackTasks(object):
    """ 回调任务
    """

    def __init__(self):
        pass

    async def start(self, *args, **kwargs):
        heart_beat_count = kwargs['heart_beat_count']
        if heart_beat_count % 60 != 0:  # 每分钟执行一次任务查询
            return
        deadline = tools.get_cur_timestamp() + 60
        while True:
            task = await callback_srv.get_task_by_deadline(deadline)
            if not task:
                return
            delay = tools.get_cur_timestamp() - task.get('deadline')
            IOLoop.current().call_later(delay, self.do_callback, task)
            logger.debug('create task:', task, caller=self)

    async def do_callback(self, task):
        """ 执行回调
        """
        logger.info('task:', task, caller=self)
        url = task.get('url')
        method = task.get('method')
        try:
            if method == 'GET':
                await AsyncHttpRequests.get(url, parse_json=False)
            elif method == 'POST':
                data = task.get('data')
                await AsyncHttpRequests.post(url=url, body=data, parse_json=False)
            else:
                logger.error('method error! task:', task, caller=self)
        except Exception as e:
            logger.error('e:', e, caller=self)
