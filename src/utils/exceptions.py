#!/usr/bin/env python
# -*- coding: utf-8 -*-

#######################################################################
#                             error const                             #
#######################################################################

MSG_OK = {'code': 0, 'msg': 'OK'}


# common errors
ERR_MSG_INVALID = {'code': 400, 'msg': 'Failed'}
ERR_MSG_WRONG_PARAMS = {'code': 400, 'msg': 'Check the params you input'}
ERR_MSG_PERMISSION_ERROR = {'code': 401, 'msg': 'Authentication failed'}
ERR_MSG_BODY_ERROR = {'code': 411, 'msg': 'Invalid body format'}
ERR_MSG_SYSTEM_ERROR = {'code': 500, 'msg': 'Internal error'}
ERR_MSG_IS_DEVELOPING = {'code': 99999, 'msg': 'TODO...'}

# paticular errors

#######################################################################
#                          custom exceptions                          #
#######################################################################


class _BaseException(Exception):
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


class ValidationError(_BaseException):
    default_msg = 'Bad Request'
    default_code = 400


class NotAuthenticated(_BaseException):
    default_msg = 'Unauthorized'
    default_code = 401


class AuthenticationFailed(_BaseException):
    default_msg = 'Forbidden'
    default_code = 403


class NotFound(_BaseException):
    default_msg = 'Not found'
    default_code = 404


class SystemError(_BaseException):
    default_msg = 'Internal Server Error'
    default_code = 500


class TimeoutException(_BaseException):
    default_msg = 'Timeout'
    default_code = 504
