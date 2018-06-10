# -*- coding:utf-8 -*-

"""
错误类型定义
Date:   2017/12/7
Update: 2017/12/22  1. 修复bug: 继承类默认msg和code失效；
        2018/03/14  1. 修改异常类型；
"""


class CustomException(Exception):
    """ 通用异常类型错误
    """
    default_msg = 'A server error occurred.'
    default_data = None
    default_code = 500

    def __init__(self, msg=None, code=None, data=None):
        self.msg = msg if msg is not None else self.default_msg
        self.code = code if code is not None else self.default_code
        self.data = data

    def __str__(self):
        str_msg = '[{code}] {msg}'.format(code=self.code, msg=self.msg)
        return str_msg


class ValidationError(CustomException):
    """ 字段校验错误
    """
    default_msg = 'Bad Request'
    default_code = 400


class NotAuthenticated(CustomException):
    """ 未授权
    """
    default_msg = 'Unauthorized'
    default_code = 401


class AuthenticationFailed(CustomException):
    """ 权限校验失败
    """
    default_msg = 'Forbidden'
    default_code = 403


class NotFound(CustomException):
    """ 未找到
    """
    default_msg = 'Not found'
    default_code = 404


class SystemError(CustomException):
    """ 系统内部错误
    """
    default_msg = 'Internal Server Error'
    default_code = 500


class TimeoutException(CustomException):
    """ 超时
    """
    default_msg = 'Timeout'
    default_code = 504
