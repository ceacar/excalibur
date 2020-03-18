import pytz
import datetime
import calendar
import time

__standard_datetime_format = '%Y-%m-%d %H:%M:%S'


def convert_timestamp_between_timezones(datetime_obj, timezone_from, timezone_to):
    """
    datetime_obj, datetime.datetime
    timezone_from:str, example: US/Eastern
    timezone_to: str, example: Utc
    return:datetiem.datetime obj of converted time at timezon_to
    """
    tz_from = pytz.timezone(timezone_from)
    tz_to = pytz.timezone(timezone_to)
    dt_from_tz = datetime_obj.replace(tzinfo=tz_from)
    dt_to_tz = dt_from_tz.astimezone(tz=tz_to)
    return dt_to_tz


def strinfy_to_standard_timezone(datetime_obj):
    return datetime_obj.strftime(__standard_datetime_format)


def get_ny_timezone_name():
    return 'US/Eastern'


def get_utc_timezone_name():
    return 'UTC'


def set_datetime_obj_timezone(datetime_object, timezone_str):
    return datetime_object.replace(tzinfo=pytz.timezone(timezone_str))


def to_unix(time_str, time_format=__standard_datetime_format):
    """
    by defaults support format of '%Y-%m-%d %H:%M:%S'
    """
    dt = datetime.datetime.strptime(time_str, time_format)
    return calendar.timegm(dt.timetuple())


def get_current_unix_time():
    return int(time.time())


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.now().strftime(date_format)


def get_current_date(date_format="%Y-%m-%d"):
    return datetime.datetime.now().strftime(date_format)


def dt_to_unix(dt_obj):
    # time.mktime will automatic do timezone conversion from your local timezone to utc timezone
    # so be aware of not passing in a non local timezone dt_obj to avoid erronous result
    return int(time.mktime(dt_obj.timetuple()))


def __from_unix_int(unix_int):
    try:
        return datetime.datetime.utcfromtimestamp(unix_int).strftime(__standard_datetime_format)
    except Exception:
        return None


def from_unix(unix_int, time_format=__standard_datetime_format):
    if len(str(unix_int)) not in [10, 13, 16, 19]:
        raise Exception("unix time format is wrong {unix_int}".format(unix_int=unix_int))

    # converts unix as unix timestamp with second
    res = __from_unix_int(unix_int)
    if not res:
        # converts as with milli second
        res = __from_unix_int(unix_int / 1000)
    if not res:
        # converts as with microsecond
        res = __from_unix_int(unix_int / 1000000)
    if not res:
        # converts as with nano
        res = __from_unix_int(unix_int / 1000000000)

    if not res:
        raise Exception("rogue unix timestamp {unix_int}".format(unix_int=unix_int))
    return res
