import excalibur
import importlib
import struct
import math
"""
proxy_parser.py is providing parser for proxy.Proxy
"""


def parse(data, port, tag):
    importlib.reload(excalibur.misc_parser)
    return excalibur.misc_parser.parse_packet(data, port, tag)


__decoder_list = ['ascii', 'utf-8', 'utf-16', 'utf-32', 'euc-kr', 'ISO-2022-KR']
__struct_type_list_8bytes = ['hhhh', 'HHHH', '8s', '2i', '2I', '2l', '2L', '2f', 'd', 'q', 'Q']
__struct_type_list_4bytes = ['hh', 'HH', 'ssss', 'i', 'I', 'l', 'L', 'f', 'd']
__struct_type_list_2bytes = ['h', 'H', 'ss']
__struct_type_list_1byte = ['c', 'b', 'B', '?']
byte_struct = {
    1: __struct_type_list_1byte,
    2: __struct_type_list_2bytes,
    4: __struct_type_list_4bytes,
    8: __struct_type_list_8bytes,
}


def unpack_this(format, data_hex):
    return struct.unpack_from(format, bytearray.fromhex(data_hex))


def parse_this(hex_data, littleendian=True):
    """
    this method would try to parse the hex data with anyformat, see what make sense
    input data_hex should be 2 byte of hex(2 digits)
    """

    iteration = math.ceil(len(hex_data) / 4)

    for i in range(1, iteration + 1):
        data_hex = hex_data[0: 4 * i]
        print('\ntrying |{}|'.format(data_hex))
        struct_prefix = '>'
        if littleendian:
            struct_prefix = '<'

        __struct_type_list = byte_struct[int(math.ceil(len(data_hex) / 2))]

        for struct_type in __struct_type_list:
            struct_type_string = struct_prefix + struct_type
            try:
                temp = struct.unpack_from(struct_type_string, bytearray.fromhex(data_hex))
                res = temp[0]
                print(struct_type_string + ': ' + str(res))
            except Exception as e:
                print(struct_type_string + ' ???? ' + str(e))

        for decoder in __decoder_list:
            try:
                print(decoder + ': ' + bytearray.fromhex(data_hex).decode(decoder))
            except Exception as e:
                print(decoder + ' ???? ' + str(e))
