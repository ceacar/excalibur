import struct
import sys


def translate_to_int(string, little_endian=True, block_size=4):
    # not works as intended
    string = string.replace(' ', '')
    result = []
    unpack_format = ''

    if little_endian:
        unpack_format += '<'
    else:
        unpack_format += '>'

    if block_size == 8:
        unpack_format += 'Q'
    elif block_size == 4:
        unpack_format += 'i'
    else:
        raise Exception('Invalid block_size')

    init_position = 0
    str_slice = string[: block_size]

    while str_slice:
        init_position += block_size
        buf = bytes(str_slice, 'utf-8')
        sys.stderr.write(buf.decode('utf-8'))
        sys.stderr.write(' ')
        value = struct.unpack_from(unpack_format, buf)[0]
        result.append(value)
        str_slice = string[init_position: init_position + block_size]
    sys.stderr.write('\n')
    res = ' '.join([str(res) for res in result])
    sys.stderr.write(res + '\n')
    return result
