import struct
import re


struct_format_length_dict = {
    'c': 1,
    's': 1,
    'h': 2,
    'H': 2,
    'i': 4,
    'I': 4,
    'l': 4,
    'L': 4,
    'q': 8,
    'Q': 8,
    'f': 4,
    'd': 8,
}


struct_types_dict = {
    # 'char': 'c',  # str and char needs decoder, so we will create dedicated method for them
    # 'str': 's',
    'short': 'h',
    'unsigned_short': 'H',
    'int': 'i',
    'unsigned_int': 'I',
    'long': 'l',
    'unsigned_long': 'L',
    'long_long': 'q',
    'unsigned_long_long': 'Q',
    'float': 'f',
    'double': 'd',
}


def __unpack_base(format, hex_string):
    res = struct.unpack_from(format, bytearray.fromhex(hex_string))
    return res


def __auto_unpack_base(format_str, hex_string, littleendian=True):
    """
    format_str: is sturct strings like 's', 'i', 'l'
    hex_string: hex plain string
    littleendian: if it is littleendian
    """

    if format_str not in struct_format_length_dict:
        raise Exception('{} not supported'.format(format_str))
    format_length = struct_format_length_dict[format_str] * 2  # result is how many bytes, so we need to multiplize by 2, since 2 hex is 1 byte

    length = int(len(hex_string) / format_length)

    format_derived = '<'
    if not littleendian:
        format_derived = '>'

    format_derived += format_str * length
    unpack_result = __unpack_base(format_derived, hex_string)

    return next(iter(unpack_result), None)


def create_unpack_functions(format_str):
    def new_unpack_func(hex_string):
        return __auto_unpack_base(format_str, hex_string)
    return new_unpack_func


def unpack_as_string(hex_string, decoder="utf-8"):
    res = __auto_unpack_base('s', hex_string)
    decoded = res.decode(decoder)
    return decoded.strip('\x00')


def unpack_as_string_GBK(hex_string, decoder="GBK"):
    byte_array_temp = bytearray.fromhex(hex_string)
    unpacked_string = [byte_array_temp[i:i+2].decode(decoder) for i in range(0, len(byte_array_temp), 2)]
    return [''.join(unpacked_string)]  # return as a list to keep consistency of method name and return types


def create_unpack_as_string_functions(decoder):
    def new_unpack_as_string(hex_string):
        return unpack_as_string(hex_string, decoder=decoder)
    return new_unpack_as_string


string_decoder_list = [
    "utf-16le",
    "utf-32",
    # "GBK",
    "GB2312",
    'euc-kr',
    'ISO-2022-KR',
]


string_unpack_funcs = {'unpack_as_string': unpack_as_string}
# dynamically create functions for different decoders
for decoder in string_decoder_list:
    func_name = 'unpack_as_string_{}'.format(decoder.replace('-', '_'))
    func = create_unpack_as_string_functions(decoder)
    globals()[func_name] = func
    string_unpack_funcs[func_name] = func


def unpack_as_decimal(hex_string):
    # will split hex string in two characters group and then translate
    try:
        return int(hex_string, 16)
    except Exception as e:
        return str(e)

def unpack_as_decimal_list(hex_string):
    # will split hex string in two characters group and then translate
    res = []
    for two_digit_hex in re.findall('..', hex_string):
        try:
            res.append(int(two_digit_hex, 16))
        except Exception as e:
            res.append(str(e))
    return res


hex_decode_functions = {'unpack_as_string': unpack_as_string}
# dynamically generate the functions
for k, v in struct_types_dict.items():
    var_name = 'unpack_as_{}'.format(k)
    func = create_unpack_functions(v)
    globals()[var_name] = func
    hex_decode_functions[var_name] = func


def try_funcs(func_dict, hex_string):
    for func_name, func in func_dict.items():
        try:
            print('{}->{}'.format(func_name, func(hex_string)))
        except Exception as e:
            print('{}->{}'.format(func_name, e))


def parse_hex_string(hex_string):
    """
    this function will iterate through almost all struct unpack from possbility to interpret the meaning of this hex_string
    """

    try_funcs(hex_decode_functions, hex_string)
    # try to interpret as decimal
    print('decimal -> {}'.format(unpack_as_decimal(hex_string)))
    res = unpack_as_decimal_list(hex_string)
    print('decimal_split_2 -> {}'.format(res))
    try_funcs(string_unpack_funcs, hex_string)
