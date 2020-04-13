import os
import excalibur
import json
import gzip

log = excalibur.logger.getlogger()


def does_file_exist_and_not_empty(data_path: str):
    """
    1. check if file exists
    2. if exists, check if size is 0
    """
    if os.path.exists(data_path):
        # if file is empty, something is wrong, we just move this file as older
        if os.stat(data_path).st_size == 0:
            return False
        else:
            return True

    return False


def does_gzip_file_exist_and_not_empty(data_path: str):
    """
    1. check if file exists
    2. if exists, check if size is 0
    """
    if os.path.exists(data_path):
        # if file is empty, something is wrong, we just move this file as older
        if os.stat(data_path).st_size < 50:
            return False
        else:
            return True

    return False


def remove_file_if_empty(data_path: str):
    if does_file_exist_and_not_empty(data_path):
        if data_path and data_path[0] != '/':
            log.info(f'Removing {data_path}')
            os.remove(data_path)


def remove_gzip_file_if_empty(data_path: str):
    if does_gzip_file_exist_and_not_empty(data_path):
        if data_path and data_path[0] != '/':
            log.info(f'Removing {data_path}')
            os.remove(data_path)


def read_file_as_json_obj(file_path: str):
    with open(file_path, 'r') as f:
        lines = f.readlines()
        line = ''.join(lines)
        return json.loads(line)


def read_gzip_file_as_json_obj(file_path: str, decoder='utf-8'):
    with gzip.open(file_path, 'rb') as f:
        lines = f.readlines()
        line = ''.join([l.decode(decoder) for l in lines])
        return json.loads(line)


def get_gzip_uncompressed_file_size(file_name):
    """
    this function will return the uncompressed size of a gzip file
    similar as gzip -l file_name
    """
    file_obj = gzip.open(file_name, 'r')
    file_obj.seek(-8, 2)
    # crc32 = gzip.read32(file_obj)
    isize = gzip.read32(file_obj)
    return isize


def write_to_gzip(file_abs_path: str, content_list: list, decoder='utf-8'):
    if type(content_list) == str:
        content_list = [content_list]

    with gzip.open(file_abs_path, 'w') as g:
        for line in content_list:
            line_to_print = str(line) + "\n"
            bline = line_to_print.encode(decoder)
            g.write(bline)


def read_from_gzip(file_abs_path: str, decoder='utf-8'):
    """
    return all file
    have memory blow up potential
    """
    res = []
    with gzip.open(file_abs_path, 'rb') as g:
        lines = g.readlines()
        for line in lines:
            res.append(line.decode(decoder))

    return res
