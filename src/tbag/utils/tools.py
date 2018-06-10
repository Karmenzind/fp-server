# -*- coding:utf-8 -*-

"""
工具包

"""

import uuid
import time
import datetime


def get_cur_timestamp():
    """ 获取当前时间戳
    """
    ts = int(time.time())
    return ts


def get_cur_datetime_m():
    """ 获取当前日期时间字符串，包含 年 + 月 + 日 + 时 + 分 + 秒 + 微妙
    """
    today = datetime.datetime.today()
    str_m = today.strftime('%Y%m%d%H%M%S%f')
    return str_m


def get_datetime():
    """ 获取日期时间字符串，包含 年 + 月 + 日 + 时 + 分 + 秒
    """
    today = datetime.datetime.today()
    str_dt = today.strftime('%Y%m%d%H%M%S')
    return str_dt


def get_date(fmt='%Y%m%d', delta_day=0):
    """ 获取日期字符串，包含 年 + 月 + 日
    @param fmt 返回的日期格式
    """
    day = datetime.datetime.today()
    if delta_day:
        day += datetime.timedelta(days=delta_day)
    str_d = day.strftime(fmt)
    return str_d


def date_str_to_dt(date_str=None, fmt='%Y%m%d', delta_day=0):
    """ 日期字符串转换到datetime对象
    @param date_str 日期字符串
    @param fmt 日期字符串格式
    @param delta_day 相对天数，<0减相对天数，>0加相对天数
    """
    if not date_str:
        dt = datetime.datetime.today()
    else:
        dt = datetime.datetime.strptime(date_str, fmt)
    if delta_day:
        dt += datetime.timedelta(days=delta_day)
    return dt


def dt_to_date_str(dt=None, fmt='%Y%m%d', delta_day=0):
    """ datetime对象转换到日期字符串
    @param dt datetime对象
    @param fmt 返回的日期字符串格式
    @param delta_day 相对天数，<0减相对天数，>0加相对天数
    """
    if not dt:
        dt = datetime.datetime.today()
    if delta_day:
        dt += datetime.timedelta(days=delta_day)
    str_d = dt.strftime(fmt)
    return str_d


def get_utc_time():
    """ 获取当前utc时间
    """
    utc_t = datetime.datetime.utcnow()
    return utc_t


def ts_to_datetime_str(ts):
    """ 将时间戳转换为日期时间格式，年-月-日 时:分:秒
    @param ts 时间戳
    """
    if not ts:
        return '00-00-00 00:00:00'
    dt = datetime.datetime.fromtimestamp(int(ts))
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def datetime_str_to_ts(dt_str, fmt='%Y-%m-%d %H:%M:%S'):
    """ 将日期时间格式字符串转换成时间戳
    @param dt_str 日期时间字符串
    @param fmt 日期时间字符串格式
    """
    ts = int(time.mktime(datetime.datetime.strptime(dt_str, fmt).timetuple()))
    return ts


def get_uuid1():
    """ make a UUID based on the host ID and current time
    """
    s = uuid.uuid1()
    return str(s)


def get_uuid3(str_in):
    """ make a UUID using an MD5 hash of a namespace UUID and a name
    @param str_in 输入字符串
    """
    s = uuid.uuid3(uuid.NAMESPACE_DNS, str_in)
    return str(s)


def get_uuid4():
    """ make a random UUID
    """
    s = uuid.uuid4()
    return str(s)


def get_uuid5(str_in):
    """ make a UUID using a SHA-1 hash of a namespace UUID and a name
    @param str_in 输入字符串
    """
    s = uuid.uuid5(uuid.NAMESPACE_DNS, str_in)
    return str(s)
