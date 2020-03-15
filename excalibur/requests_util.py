import requests
import datetime
import sys
import urllib
import excalibur

__requests_timestamp_format = '%a, %d %b %Y %H:%M:%S %Z'
log_ins = excalibur.logger.getlogger()


def get_remote_file_header(url, auth=None):
    header_info = requests.head(url, auth=auth)
    return header_info.headers


def get_remote_file_timestamp(url, auth=None):
    """
    get remote file timestamp, returns a datetime obj
    """
    header_info = get_remote_file_header(url, auth=auth)
    mod_time = header_info['Last-Modified']
    dt_obj = datetime.datetime.strptime(mod_time, __requests_timestamp_format)
    return dt_obj


def download_progress(count, blockSize, totalSize):
    percent = int(count * blockSize * 100 / totalSize)
    sys.stdout.write("\r" + ">>...%d%%" % percent)
    sys.stdout.flush()


def download_file(url: str, file_abs_path: str):
    log_ins.info(f"Downloading {url} -> {file_abs_path}\n")
    download_path, _ = urllib.request.urlretrieve(url, file_abs_path, download_progress)
    log_ins.info("\n")
