# -*- coding:utf-8 -*-

"""
tornado实现的HTTP异步非阻塞客户端

Date:   2017/07/31
Update: 2017/09/19  1. 增加对POST请求body的编码格式区分;
        2017/09/26  1. 增加请求超时时间;
        2017/11/21  1. 增加对返回结果decode_type为空的判断;
        2017/12/26  1. 修复bug: 引入被删除的模块;
"""

import json

from tornado.httpclient import AsyncHTTPClient
from tornado.httputil import url_concat, urlencode

from tbag.core import exceptions
from tbag.utils import log as logger


class AsyncHttpRequests(object):
    """ HTTP异步请求封装
    """

    @classmethod
    async def get(cls, url, params=None, headers=None, decode_type='utf-8', parse_json=True, timeout=30):
        """ HTTP GET 请求
        @param url 请求url
        @param params 请求的uri qurey参数
        @param headers 请求的header参数
        @param decode_type 返回body解码格式，默认使用utf-8解码
        @param parse_json 是否解析返回body为json格式，默认为True
        @param timeout 请求超时时间，默认30秒
        @return data 返回的http body
        """
        if params:
            url = url_concat(url, params)
        http_client = AsyncHTTPClient()
        response = await http_client.fetch(url, method='GET', headers=headers, request_timeout=timeout)
        if response.code not in (200, 201, 202, 203, 204, 205, 206):
            logger.error('url:', url, 'response code:', response.code, 'response body:', response.body, caller=cls)
            msg = '请求url失败: {url}'.format(url=url)
            raise exceptions.CustomException(msg=msg)
        if response.body:
            data = response.body
            if decode_type:
                data = data.decode(decode_type)
            if parse_json:
                return json.loads(data)
            else:
                return data
        else:
            return None

    @classmethod
    async def post(cls, url, params=None, body=None, headers=None, encode_type='utf-8', decode_type='utf-8',
                   parse_json=True, timeout=30):
        """ HTTP POST 请求
        @param url 请求url
        @param params 请求的uri qurey参数
        @param body 请求的body参数
        @param headers 请求的header参数
        @param encode_type 请求body编码格式，默认使用utf-8编码
        @param decode_type 返回body解码格式，默认使用utf-8解码
        @param parse_json 是否解析返回body为json格式，默认为True
        @param timeout 请求超时时间，默认30秒
        @return data 返回的http body
        """
        if params:
            url = url_concat(url, params)
        if body:
            if not encode_type:
                pass
            elif encode_type == 'utf-8':
                body = json.dumps(body)
            else:
                body = urlencode(body, encoding=encode_type)
        http_client = AsyncHTTPClient()
        response = await http_client.fetch(url, method='POST', body=body, headers=headers, request_timeout=timeout)
        if response.code not in (200, 201, 202, 203, 204, 205, 206):
            logger.error('url:', url, 'post data:', body, 'response code:', response.code, 'response body:',
                         response.body, caller=cls)
            msg = '请求url失败: {url}'.format(url=url)
            raise exceptions.CustomException(msg=msg)
        if response.body:
            data = response.body
            if decode_type:
                data = data.decode(decode_type)
            if parse_json:
                return json.loads(data)
            else:
                return data
        else:
            return None
