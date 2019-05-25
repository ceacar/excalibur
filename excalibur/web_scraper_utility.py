import sys
from .string_manipulation import *

import pdb

import requests
import shutil
import os

__temp_path = '~/temp'
def extract_file_name_from_url(url):
    return url.split('/')[-1]

def download_image_from_url(url):
    r = requests.get(url, stream=True)
    file_name = extract_file_name_from_url(url)
    file_path = '{path}/{name}'.format(path=__temp_path, name=file_name)
    file_path = os.path.expanduser(file_path)

    #pdb.set_trace()
    if r.status_code == 200:
        with open(file_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

def __process_chou_shushu(long_str):
    splitted_str_arr = long_str.split("url(")
    res = []

    for line in splitted_str_arr:
        if 'https' not in line:
            continue
        res.append(line.split(")}")[0])
    return res


def extract_https_urls_from_src(input_src):
    res = []
    for line in input_src:
        res.append(line)
    res_to_process = ''.join(res)
    process_arr = __process_chou_shushu(res_to_process)
    return process_arr

def extract_https_urls_from_src_using_regex(input_src):
    res = []
    import re
    for line in input_src:
        res.append(line)
    res_to_process = ''.join(res)


    all_match = re.findall('https://static.wixstatic.com(.+?)webp', res_to_process)
    urls = []

    for match in all_match:
        if '</div>' in match:
            continue
        urls.append('https://static.wixstatic.com{match}webp'.format(match=match))
    #pdb.set_trace()

    return urls



def download_images_from_choushushu(input_src):
    res = extract_https_urls_from_src_using_regex(input_src)
    for url in res:
        download_image_from_url(url)
