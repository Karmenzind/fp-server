# -*- coding: utf-8 -*-

import datetime
import re

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
