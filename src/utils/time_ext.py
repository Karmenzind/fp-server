# -*- coding: utf-8 -*-

import datetime
import re
import time

ZERO_TIME_DELTA = datetime.timedelta(0)
LOCAL_TIME_DELTA = datetime.timedelta(hours=8)  # 本地时区偏差


class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return ZERO_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA


class LocalTimeZone(datetime.tzinfo):
    def utcoffset(self, dt):
        return LOCAL_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA

    def tzname(self, dt):
        return '+08:00'


# singleton
UTC = UTC()
LocalTimeZone = LocalTimeZone()

date_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$'
)

datetime_re = re.compile(
    r'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})'
    r'[T ](?P<hour>\d{1,2}):(?P<minute>\d{1,2})'
    r'(?::(?P<second>\d{1,2})(?:\.(?P<microsecond>\d{1,6})\d{0,6})?)?'
    r'(?P<tzinfo>Z|[+-]\d{2}(?::?\d{2})?)?$'
)


def parse_date(value):
    """Parses a string(ISO_8601) and return a datetime.date.

    Raises ValueError if the input is well formatted but not a valid date.
    Returns None if the input isn't well formatted.
    """
    match = date_re.match(value)
    if match:
        kw = {k: int(v) for k, v in match.groupdict().items()}
        return datetime.date(**kw)


def parse_datetime(value):
    """Parses a string(ISO_8601) and return a datetime.datetime base UTC,
    or parse datetime.datetime base other timezone and return a datetime.datetime base UTC timezone
    """
    if isinstance(value, datetime.datetime):
        if not value.tzinfo:
            value = value.replace(tzinfo=LocalTimeZone)
        return value.astimezone(UTC)

    match = datetime_re.match(value)
    if match:
        kw = match.groupdict()
        if kw['microsecond']:
            kw['microsecond'] = kw['microsecond'].ljust(6, '0')
        tzinfo = kw.pop('tzinfo')
        tz = UTC
        offset = 0
        if tzinfo == 'Z':
            offset = 0
        elif tzinfo is not None:
            offset_mins = int(tzinfo[-2:]) if len(tzinfo) > 3 else 0
            offset = 60 * int(tzinfo[1:3]) + offset_mins
            if tzinfo[0] == '-':
                offset = -offset
        else:
            tz = LocalTimeZone
        kw = {k: int(v) for k, v in kw.items() if v is not None}
        kw['tzinfo'] = tz
        dt = datetime.datetime(**kw)
        dt += datetime.timedelta(minutes=offset)
        return dt.astimezone(UTC)


def convert_zone(dt: datetime.datetime, tz_to=UTC, tz_default=LocalTimeZone):
    """
    @param dt:
    @param tz_to: 转换后的目标时区
    @param tz_default: dt无时区信息时的默认时区
    """
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=tz_default)
    return dt.astimezone(tz_to)


def get_utc_time(dt: datetime.datetime = None, tz_default=LocalTimeZone):
    """
    @param dt 为None时，返回当前时间
    @param tz_default dt无时区信息时的默认时区
    """
    if dt is None:
        dt = datetime.datetime.now()
    return convert_zone(dt, tz_default=tz_default)


def get_time_str(dt: datetime.datetime = None, tz_default=LocalTimeZone):
    """
    @param dt 为None时，返回当前时间
    @param tz_default dt无时区信息时的默认时区
    """
    if not dt:
        dt = datetime.datetime.now()
    dt = convert_zone(dt, tz_default=tz_default)
    time_str = dt.isoformat().split('+')[0]
    return time_str + 'Z'


def get_date_str(dt: datetime.date = None):
    """
    @param dt 为None时，返回当前日期
    """
    if not dt:
        dt = datetime.date.today()
    return dt.isoformat()


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


def current_timestamp(_int=True):
    res = time.time()
    if _int:
        res = int(res)
    return res
