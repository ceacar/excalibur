import excalibur
import sys
import base64


def dec(inp):
    return excalibur.hex_utility.unpack_as_decimal(inp)


def hex_to_bit(hex_string):
    return bin(int('e678', 16))


def check_utf8_length(hex_input, littlendian=True):
    """
    utf-8 has variable length from 1 byte up to 4bytes

    takes in 8 string hex (4 bytes)
    output length of utf-encoding, if no length can be specified, return -1

    UTF-8 variable length bytes obeys below rules:
        1byte would have pattern
        1110 xxxx
        each subsequent byte wold have
        0100 0000

        so to detech length of utf-8
        just filter the bytes with

        so for 4 bytes sequence
        filter bytes should look like f8 c0 c0 c0
        filter -> (f)1111 (8)1000 (c)1100 (0)0000 (c)1100 (0)0000
        and we expect f0 80 80 80 80
        output -> (f)1111 (0)0000 (c)1100 (0)0000 (c)1100 (0)0000

        for 3 bytes
        we expect e0c0c0 for output
        filter bytes should look like f8 c0 c0 c0
        filter -> (f)1111 (8)1000 (c)1100 (0)0000 (c)1100 (0)0000
        and we expect f0 80 80 80 80
        output -> (e)1110 (0)0000 (c)1100 (0)0000 (c)1100 (0)0000

        for 2 bytes
        we expect e0c0 for output
    """

    length = len(hex_input)
    if length < 2 or length % 2 > 0:
        return -1

    # assume input is hex str list
    hex_input_list = [hex_input[i:i+2] for i in range(0, len(hex_input), 2)]
    decimal_input_list = [dec(hex_input) for hex_input in hex_input_list]

    decimal_list_length = len(decimal_input_list)

    if decimal_list_length == 4 and decimal_input_list[0] & dec("0xF8") == dec("0xF0") \
        and decimal_input_list[1] & dec("0xC0") == dec("0x80") \
        and decimal_input_list[2] & dec("0xC0") == dec("0x80") \
        and decimal_input_list[3] & dec("0xC0") == dec("0x80"):
            # start of 4-byte sequence
            return 4

    if decimal_list_length == 3 and decimal_input_list[0] & dec("0xF0") == dec("0xE0") \
        and decimal_input_list[1] & dec("0xC0") == dec("0x80") \
            and decimal_input_list[2] & dec("0xC0") == dec("0x80"):
            # start of 3-byte sequence
            return 3

    if decimal_list_length == 2 and decimal_input_list[0] & dec("0xE0") == dec("0xC0") \
            and decimal_input_list[1] & dec("0xC0") == dec("0x80"):
            # start of 2-byte sequence
            return 2

    if decimal_list_length == 1 and decimal_input_list[0] & dec("0x80") == dec("0x00"):
        return 1

    # all condition has tried, seems not utf-8
    return -1


def check_utf16_length(input_hex_str, littleendian=True):
    """
    func will check length of bytes input no matter how long it is, it always just check first few bytes that can is a byte sequence

    utf-16 2 bytes has no distinguish pattern

	Scalar Value UTF-16
	xxxxxxxxxxxxxxxx(2bytes)         xxxxxxxx xxxxxxxx
	000uuuuuxxxxxxxxxxxxxxxx(4bytes) 110110ww wwxxxxxx 110111xx xxxxxxxx
    """

    length = len(input_hex_str)
    if length < 4:
        return -1

    BOM = 'feff'

    indice_orders = [0, 1, 2, 3]
    if littleendian:
        BOM = 'fffe'
        indice_orders = [1, 0, 3, 2]


    # skip BOM
    byte_sequence_length_base = 0  # 2 bytes are included in the BOM
    if input_hex_str[:4] == BOM:
        byte_sequence_length_base = 2  # 2 bytes are included in the BOM
        input_hex_str = input_hex_str[4:]

    hex_input_list = [input_hex_str[i:i+2] for i in range(0, length, 2)]
    decimal_input_list = [dec(hex_input) for hex_input in hex_input_list]
    decimal_list_length = len(decimal_input_list)

    # we only need to check 4 bytes situtition
    # check first byte has 110110xx ????????  ( 8+16+64+128)
    if length >= 8 and \
       decimal_input_list[indice_orders[0]] & dec("0xFC") == dec("0xD8") and \
       decimal_input_list[indice_orders[2]] & dec("0xFC") == dec("0xDC"):
        return 4 + byte_sequence_length_base

    # if it is 2 bytes, there is nothing to check
    if length == 4:
        return 2 + byte_sequence_length_base

    # utf-16 only have 2 bytes or 4 bytes case
    return -1


def check_gbk_length(input_hex_str, littleendian=True):
    """
	A character is encoded as 1 or 2 bytes.
	A byte in the range 00–7F is a single byte that means the same thing as it does in ASCII.
	Strictly speaking, there are 95 characters and 33 control codes in this range.

	A byte with the high bit set indicates that it is the first of 2 bytes.
	Loosely speaking, the first byte is in the range 81–FE (that is, never 80 or FF), and the second byte is 40–A0 except 7F for some areas and A1–FE for others.
	"""
    length = len(input_hex_str)
    if length < 2:
        return -1

    # skip BOM
    hex_input_list = [input_hex_str[i:i+2] for i in range(0, length, 2)]
    decimal_input_list = [dec(hex_input) for hex_input in hex_input_list]

    # TODO:still doesn't know what the order would be like for littleendian and big endian in gbk encoding
    indice_orders = [0, 1]

    # we only need to check 4 bytes situtition
    # if first byte has highest bit set to 1, we know it is a 2 byte sequence
    if length >= 4 and decimal_input_list[indice_orders[0]] & dec("0x80") == dec("0x80"):
        return 2

    return 1


def _decode_utf8_with_auto_length_detection(input_hex_str, littleendian=True):
    """
    recursively finds the utf-8 byte length and then decode accordingly
    utf8 doesn't have endian problem. but still put the littleendian option parameter to keep consistency
    """

    if not input_hex_str:
        return ''

    # skip BOM
    if input_hex_str[:6] == 'efbbbf':
        sys.stderr.write('\nremoved header efbbbf from {}\n'.format(input_hex_str))
        input_hex_str=input_hex_str[6:]

    length = len(input_hex_str)

    if len(input_hex_str) % 2 > 0:
        raise ValueError('input length is not even, cannot decode')

    # input_hex_str is even
    # now we decode one byte or many byte at a time depends on what's the length
    byte_sequence_length = check_utf8_length(input_hex_str)


    # we have recursively hit the end of input hex, so we decode the byte/bytes
    if len(input_hex_str) == byte_sequence_length * 2:
        # now we finally get only the bytes suit the byte_sequence length, we will decode
        try:
            res = bytearray.fromhex(input_hex_str).decode('utf-8')
            return res
        except:
            return '?'

    if byte_sequence_length < 0:
        # this input is invalid, so will just ignore this 1 byte
        current_decoded = '?'
        input_hex_str = input_hex_str[2:]
        future_decoded = _decode_utf8_with_auto_length_detection(input_hex_str)
        return current_decoded + future_decoded


    # we have not hit the end of recursion, so we continue the recursion
    if len(input_hex_str) > byte_sequence_length * 2:
        # when there is still input, we will decode
        # we will crop the input_hex_str and then try to decode
        to_decode = input_hex_str[:2 * byte_sequence_length]
        current_decoded = _decode_utf8_with_auto_length_detection(to_decode)
        input_hex_str = input_hex_str[2 * byte_sequence_length:]
        print(input_hex_str)
        future_decoded = _decode_utf8_with_auto_length_detection(input_hex_str)
        return current_decoded + future_decoded

    if len(input_hex_str) < byte_sequence_length * 2:
        raise Exception('should not be here, unless check length function is wrong')


def decode_utf8_with_auto_length_detection(input_hex_str, littleendian=True):
    res = _decode_utf8_with_auto_length_detection(input_hex_str, littleendian=littleendian)
    return res.strip('\x00')  # sanitize results, 00 will be decoded as \x00


def decode_utf16_with_auto_length_detection(input_hex_str, littleendian=True):
    """
    it will use length detection to decode 1 byte sequence at a time
    when there is decode failure, move 1 byte to the right.
    But utf-16 seems have a very wide range of decode, which will take in most of error
    """
    # 'fffe43d8bcdf'
    # 1. there is bom
    # 2. there is no bom
    if not input_hex_str:
        return ''

    length = len(input_hex_str)
    if length < 4:
        # utf16 can have 2bytes up to how many?
        sys.stderr.write('invalid length to decode as utf16')
        return '?'

    decoder = 'utf-16'
    if littleendian:
        bom = 'fffe'
        decoder = 'utf-16le'
    else:
        bom = 'feff'

    # remove bom since utf-16le doesn't digest it well
    if input_hex_str[:4] == bom:
        input_hex_str = input_hex_str[4:]

    byte_sequence_length = check_utf16_length(input_hex_str)

    # input is not valid utf16 hex, remove 1 byte from input, see if next byte make sense
    if byte_sequence_length < 0:
        # TODO: debate whether we should jump 1 byte a time or 2 bytes at a time
        input_hex_str = input_hex_str[2:]
        return decode_utf16_with_auto_length_detection(input_hex_str)

    # we've hit recursive end, we need to decode it
    if byte_sequence_length * 2 == len(input_hex_str):
        return bytearray.fromhex(input_hex_str).decode(decoder)

    to_decode = input_hex_str[:byte_sequence_length * 2]
    try:
        current_decoded = decode_utf16_with_auto_length_detection(to_decode)
        future_decode = input_hex_str[byte_sequence_length * 2:]
    except:
        current_decoded = '?'
        # if decode failed, move 1 byte to the right
        future_decode = input_hex_str[2:]

    future_decoded = decode_utf16_with_auto_length_detection(future_decode)
    return current_decoded + future_decoded


def _decode_gbk_with_auto_length_detection(input_hex_str, littleendian=True):
    """
    recursively finds the utf-8 byte length and then decode accordingly, this trusts input_hex_str is precisely gbk,
    gbk can't find any endian related information.
    """
    if not input_hex_str:
        return ''

    length = len(input_hex_str)

    if len(input_hex_str) % 2 > 0:
        raise ValueError('input length is not even, cannot decode')

    byte_sequence_length = check_gbk_length(input_hex_str)

    # we have recursively hit the end of input hex, so we decode the byte/bytes
    if len(input_hex_str) == byte_sequence_length * 2:
        # now we finally get only the bytes suit the byte_sequence length, we will decode
        try:
            res = bytearray.fromhex(input_hex_str).decode('gbk')
            return res
        except:
            return '?'

    # we have not hit the end of recursion, so we continue the recursion
    if len(input_hex_str) > byte_sequence_length * 2:
        # when there is still input, we will decode
        # we will crop the input_hex_str and then try to decode
        to_decode = input_hex_str[:2 * byte_sequence_length]
        current_decoded = _decode_gbk_with_auto_length_detection(to_decode)
        input_hex_str = input_hex_str[2 * byte_sequence_length:]
        future_decoded = _decode_gbk_with_auto_length_detection(input_hex_str)
        return current_decoded + future_decoded

    if len(input_hex_str) < byte_sequence_length * 2:
        raise Exception('should not be here, unless check length function is wrong')


def decode_gbk_with_auto_length_detection(input_hex_str, littleendian=True):
    res = _decode_gbk_with_auto_length_detection(input_hex_str, littleendian=littleendian)
    return res.strip('\x00')


def _brute_force_base(decode_func, input_hex_str, littleendian=True):
    """
    input is variable length of hex string.
    it will try different length of hex for decoding
    1. this string maybe feed with a partial byte, so we iterate one hex(half byte) at a time
    """
    # add a 0 at the top would cover all cases for partial string
    input_hex_str = '0' + input_hex_str

    translated_msgs = []

    for i in range(0, len(input_hex_str)):
        to_decode = input_hex_str[i:]

        if len(to_decode) % 2 > 0:
            # put a 0 in the end to make it a even length
            to_decode = to_decode + '0'

        try:
            res = decode_func(to_decode, littleendian)
        except Exception:
            res = ''
        if res:
            translated_msgs.append('{} <- {}'.format(res, to_decode))

    # translated_msgs.reverse()
    for msg in translated_msgs:
        print(msg)


def brute_force_partial_utf16(input_hex_str, littleendian=True):
    """
    input is variable length of hex string.
    it will try different length of hex for decoding
    1. this string maybe feed with a partial byte, so we iterate one hex(half byte) at a time
    """
    _brute_force_base(decode_utf16_with_auto_length_detection, input_hex_str, littleendian)


def brute_force_partial_utf8(input_hex_str, littleendian=True):
    """
    input is variable length of hex string.
    it will try different length of hex for decoding
    1. this string maybe feed with a partial byte, so we iterate one hex(half byte) at a time
    """

    _brute_force_base(decode_utf8_with_auto_length_detection, input_hex_str, littleendian)

def brute_force_partial_gbk(input_hex_str, littleendian=True):
    """
    input is variable length of hex string.
    it will try different length of hex for decoding
    1. this string maybe feed with a partial byte, so we iterate one hex(half byte) at a time
    """
    _brute_force_base(decode_gbk_with_auto_length_detection, input_hex_str, littleendian)

def decode_as_decimal_brute_force(hex_input, littleendian = True):
    hex_input_list = [hex_input[i:i+2] for i in range(0, len(hex_input), 2)]
    decimal_input_list = [dec(hex_input) for hex_input in hex_input_list]
    return decimal_input_list


def decode_brute_force(input_hex_str, littleendian = True):
    print('utf-8')
    brute_force_partial_utf8(input_hex_str, littleendian)
    print('utf-16')
    brute_force_partial_utf16(input_hex_str, littleendian)
    print('gbk')
    brute_force_partial_gbk(input_hex_str, littleendian)
    print('decimal')
    print(decode_as_decimal_brute_force(input_hex_str, littleendian))


def encode_base64(message:str):
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode()


def decode_base64(message:str):
    message_bytes = bytes(message, 'ascii')
    return base64.b64decode(message_bytes)
