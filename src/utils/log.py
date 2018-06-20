# -*- coding:utf-8 -*-

"""
日志打印
"""

import logging
import os
import sys

from tornado import log
from tornado.options import options


def initLogger(log_level='debug', log_path=None, logfile_name=None):
    """ 初始化日志输出
    @param log_level 日志级别 debug info
    @param log_path 日志输出路径
    @param logfile_name 日志文件名
    """

    if log_level == 'info':
        options.logging = 'info'
    else:
        options.logging = 'debug'
    logger = logging.getLogger()

    if logfile_name:
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        logfile = os.path.join(log_path, logfile_name)
        print('init logger ...:', logfile)
        handler = logging.handlers.TimedRotatingFileHandler(
            logfile, 'midnight')
    else:
        handler = logging.StreamHandler()
    fmt_str = '%(levelname)1.1s [%(asctime)s] %(message)s'
    fmt = log.LogFormatter(fmt=fmt_str, datefmt=None)
    handler.setFormatter(fmt)
    logger.addHandler(handler)


def info(*args, **kwargs):
    func_name, kwargs = _log_msg_header(*args, **kwargs)
    logging.info(_log(func_name, *args, **kwargs))


def warn(*args, **kwargs):
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.warning(_log(msg_header, *args, **kwargs))


def debug(*args, **kwargs):
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.debug(_log(msg_header, *args, **kwargs))


def error(*args, **kwargs):
    logging.error('*' * 40)
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.error(_log(msg_header, *args, **kwargs))
    logging.error('*' * 40)


exception = error


def _log(msg_header, *args, **kwargs):
    _log_msg = msg_header

    for l in args:
        if type(l) == tuple:
            ps = str(l)
        else:
            try:
                ps = '%r' % l
            except:
                ps = str(l)

        if type(l) == str:
            _log_msg += ps[1:-1] + ' '
        else:
            _log_msg += ps + ' '

    if len(kwargs) > 0:
        _log_msg += str(kwargs)

    return _log_msg


def _log_msg_header(*args, **kwargs):
    """ 打印日志的message头
    @param kwargs['caller'] 调用的方法所属类对象
    @param kwargs['session_id'] 调用的方法所带的session_id
    * NOTE: logger.xxx(... caller=self) for instance method
            logger.xxx(... caller=cls) for @classmethod
    """
    cls_name = ''
    func_name = sys._getframe().f_back.f_back.f_code.co_name
    session_id = '-'
    try:
        _caller = kwargs.get('caller', None)

        if _caller:
            if not hasattr(_caller, '__name__'):
                _caller = _caller.__class__
            cls_name = _caller.__name__
            del kwargs['caller']
        session_id = kwargs.get('session_id', '-')

        if session_id:
            del kwargs['session_id']
    except:
        pass
    finally:
        msg_header = f'[{cls_name}.{func_name}] [{session_id}] '

        return msg_header, kwargs
