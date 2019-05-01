import pytz

__standard_datetime_format = '%Y-%m-%d %H:%M:%S'


def convert_timestamp_between_timezones(datetime_obj, timezone_from, timezone_to):
    """
    datetime_obj, datetime.datetime
    timezone_from:str
    timezone_to: str
    return:datetiem.datetime obj of converted time at timezon_to
    """
    tz_from = pytz.timezone(timezone_from)
    tz_to = pytz.timezone(timezone_to)
    dt_from_tz = datetime_obj.replace(tzinfo=tz_from)
    dt_to_tz = dt_from_tz.astimezone(tz=tz_to)
    return dt_to_tz


def converts_to_standard_timezone(datetime_obj):
    return datetime_obj.strptime(__standard_datetime_format)


def get_ny_timezone_name():
    return 'US/Eastern'


def get_utc_timezone_name():
    return 'UTC'


def set_datetime_obj_timezone(datetime_object, timezone_str):
    return datetime_object.replace(tzinfo=pytz.timezone(timezone_str))
