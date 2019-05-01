import requests
import datetime

__requests_timestamp_format = '%a, %d %b %Y %H:%M:%S %Z'


def get_remote_file_header(url, auth=None):
    header_info = requests.head(url, auth=auth)
    return header_info


def get_remote_file_timestamp(url, auth=None):
    """
    get remote file timestamp, returns a datetime obj
    """
    header_info = get_remote_file_header(url, auth=auth)
    mod_time = header_info['Last-Modified']
    dt_obj = datetime.datetime.strptime(mod_time, __requests_timestamp_format)
    return dt_obj
