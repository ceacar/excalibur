#!/usr/bin/env python
import multiprocessing as mp
import os
import random
import string
import sys


__nproc = mp.cpu_count()


def _process_wrapper(input_file_name, chunkStart, chunkSize, process_func):
    with open(input_file_name, 'r') as f:
        f.seek(chunkStart)
        lines = f.read(chunkSize).splitlines()
        for line in lines:
            process_func(line)
        return "{start}-{end} processed".format(start = chunkStart, end = chunkStart + chunkSize)


def _save_chunks(input_file_name, chunkStart, chunkSize, process_func, output_file_name):
    with open(input_file_name, 'r') as f:
        f.seek(chunkStart)
        lines = f.read(chunkSize).splitlines()
        for line in lines:
            with open(output_file_name, 'w') as output_file:
                output_file.write(line)
        return "{start}-{end} written".format(start = chunkStart, end = chunkStart + chunkSize)


def _chunkify(fname,size=1024*1024):
    fileEnd = os.path.getsize(fname)
    with open(fname,'r') as f:
        chunkEnd = f.tell()
        while True:
            chunkStart = chunkEnd
            f.seek(size + chunkStart, 0)
            f.readline()
            chunkEnd = f.tell()
            yield chunkStart, chunkEnd - chunkStart
            if chunkEnd > fileEnd:
                break


def process_large_file(input_file_name, process_func, size):
    pool = mp.Pool(__nproc)
    jobs = []

    #create jobs
    for chunkStart,chunkSize in _chunkify(input_file_name, size):
        print(chunkStart,chunkSize)
        jobs.append(pool.apply_async(_process_wrapper,(input_file_name, chunkStart,chunkSize, process_func)) )

    #wait for all jobs to finish
    return_result_array = []
    for job in jobs:
        return_result_array.append(job.get())

    #clean up
    pool.close()


def __pick_file_name(fname, sequence_number):
    fname_arr = fname.split('.') #  assume file has appendix like a.csv
    output_file_name = f'{".".join(fname_arr[:-1])}.{sequence_number}.{fname_arr[-1]}'
    return output_file_name


def __save_lines(input_fname, sequence_number, start, read_size):
    output_file_name = __pick_file_name(input_fname, sequence_number)
    with open(input_fname, 'r') as ifile:
        ifile.seek(start)
        with open(output_file_name, 'w') as wfile:
            content = ifile.read(read_size)
            wfile.write(content)


def split_large_file(fname, size = 1024*1024):
    """
    input:
    fname(file name), size(size of splitted_file)

    how it works
    Assume file name is f_name.csv
    will split file into f_name.0.csv, f_name.1.csv ...
    """
    fileEnd = os.path.getsize(fname)
    sequence_number = 0
    with open(fname,'r') as f:
        chunkEnd = f.tell()
        while True:
            chunkStart = chunkEnd
            f.seek(size + chunkStart, 0)
            f.readline()
            chunkEnd = f.tell()
            __save_lines(fname, sequence_number, chunkStart, chunkEnd - chunkStart)
            if chunkEnd > fileEnd:
                break
            sequence_number += 1

#example of how to use multiprocessing
#if __name__ == '__main__':
#    import argparse
#    parser = argparse.ArgumentParser()
#    parser.add_argument("file_name", help = "file full abs path with name", type = str) # type is defaulted to str
#    parser.add_argument("size", help = "chunk byte size", type = str) # type is defaulted to str
#    args = parser.parse_args()
#
#    def _print_operation(x):
#        print('processing {0}'.format(x))
#    process_large_file(args.file_name, _print_operation, int(args.size))
