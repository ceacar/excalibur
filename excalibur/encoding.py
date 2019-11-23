import excalibur
import sys


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

    if decimal_input_list[0] & dec("0xF8") == dec("0xF0") \
        and decimal_input_list[1] & dec("0xC0") == dec("0x80") \
        and decimal_input_list[2] & dec("0xC0") == dec("0x80") \
        and decimal_input_list[3] & dec("0xC0") == dec("0x80"):
            # start of 4-byte sequence
            return 4

    if decimal_input_list[0] & dec("0xF0") == dec("0xE0") \
        and decimal_input_list[1] & dec("0xC0") == dec("0x80") \
            and decimal_input_list[2] & dec("0xC0") == dec("0x80"):
            # start of 3-byte sequence
            return 3

    if decimal_input_list[0] & dec("0xE0") == dec("0xC0") \
            and decimal_input_list[1] & dec("0xC0") == dec("0x80"):
            # start of 2-byte sequence
            return 2

    if decimal_input_list[0] & dec("0x80") == dec("0x00"):
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

    # we only need to check 4 bytes situtition
    # check first byte has 110110xx ????????  ( 8+16+64+128)
    if length >= 8 and \
       decimal_input_list[indice_orders[0]] & dec("0xFC") == dec("0xD8") and \
       decimal_input_list[indice_orders[2]] & dec("0xFC") == dec("0xDC"):
        return 4 + byte_sequence_length_base

    # if it is 2 bytes, there is nothing to check
    return 2 + byte_sequence_length_base


def decode_utf8_with_auto_length_detection(input_hex_str):
    """
    recursively finds the utf-8 byte length and then decode accordingly
    """
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
        future_decoded = decode_utf8_with_auto_length_detection(input_hex_str)
        return current_decoded + future_decoded


    # we have not hit the end of recursion, so we continue the recursion
    if len(input_hex_str) > byte_sequence_length * 2:
        # when there is still input, we will decode
        # we will crop the input_hex_str and then try to decode
        to_decode = input_hex_str[:2 * byte_sequence_length]
        current_decoded = decode_utf8_with_auto_length_detection(to_decode)
        input_hex_str = input_hex_str[2 * byte_sequence_length:]
        future_decoded = decode_utf8_with_auto_length_detection(input_hex_str)
        return current_decoded + future_decoded

    if len(input_hex_str) < byte_sequence_length * 2:
        raise Exception('should not be here, unless check length function is wrong')


def decode_utf16_with_auto_length_detection(input_hex_str, littleendian=True):
    """
    it will use length detection to decode 1 byte sequence at a time
    when there is decode failure, move 1 byte to the right.
    But utf-16 seems have a very wide range of decode, which will take in most of error
    """
    # 'fffe43d8bcdf'
    # 1. there is bom
    # 2. there is no bom

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


def _brute_force_base(decode_func, input_hex_str, littleendian=True):
    """
    input is variable length of hex string.
    it will try different length of hex for decoding
    1. this string maybe feed with a partial byte, so we iterate one hex(half byte) at a time
    """
    if len(input_hex_str) % 2 > 0:
        # put a 0 in the end to make it a even length
        input_hex_str = input_hex_str + '0'

    for i in range(0, len(input_hex_str), 2):
        to_decode = input_hex_str[i:]
        try:
            res = decode_func(to_decode, littleendian)
        except Exception:
            res = ''
        if res:
            print('{} <- {}'.format(res, to_decode))


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


def decode_brute_force(input_hex_str, littleendian = True):
    print('utf-8')
    brute_force_partial_utf8(input_hex_str, littleendian)
    print('utf-16')
    brute_force_partial_utf16(input_hex_str, littleendian)


def decode_as_decimal_brute_force(hex_input, littleendian = True):
    hex_input_list = [hex_input[i:i+2] for i in range(0, len(hex_input), 2)]
    decimal_input_list = [dec(hex_input) for hex_input in hex_input_list]
    return decimal_input_list


class EncodingDetectFile:
    ENCODING_ASCII = 'ascii'
    ENCODING_UTF_8 = 'utf_8'
    ENCODING_UTF_16_BE = 'utf_16_be'
    ENCODING_UTF_16_LE = 'utf_16_le'

    # http://unicode.org/faq/utf_bom.html#BOM
    BOM_UTF_8 = '\xef\xbb\xbf'
    BOM_UTF_16_BE = '\xfe\xff'
    BOM_UTF_16_LE = '\xff\xfe'

    BYTE_EOL = (13,10) # \r\n

    UTF_16_NULL_PERCENT_POSITIVE = 0.7
    UTF_16_NULL_PERCENT_NEGATIVE = 0.1

    def _detect_bom(self,fh):
        def result(encoding,bom_marker):
            return (encoding,bom_marker,None)

        # test 2 byte UTF-16 BOMs
        file_data = bytearray(fh.read(2))
        if (file_data == EncodingDetectFile.BOM_UTF_16_BE):
            return result(
                EncodingDetectFile.ENCODING_UTF_16_BE,
                EncodingDetectFile.BOM_UTF_16_BE
            )

        if (file_data == EncodingDetectFile.BOM_UTF_16_LE):
            return result(
                EncodingDetectFile.ENCODING_UTF_16_LE,
                EncodingDetectFile.BOM_UTF_16_LE
            )

        # test 3 byte UTF-8 BOM
        file_data.append(fh.read(1))
        if (file_data == EncodingDetectFile.BOM_UTF_8):
            return result(
                EncodingDetectFile.ENCODING_UTF_8,
                EncodingDetectFile.BOM_UTF_8
            )

        # no BOM marker - return bytes read so far
        return False,False,file_data

    def _detect_ascii_utf8(self,file_data):
        ascii_chars_only = True

        byte_follow = 0
        for file_byte in file_data:
            # process additional character byte(s)
            if (byte_follow):
                if (128 <= file_byte <= 191):
                    byte_follow -= 1
                    ascii_chars_only = False
                    continue

                # not ASCII or UTF-8
                return False

            # determine byte length of character
            # https://en.wikipedia.org/wiki/UTF-8#Codepage_layout
            if (1 <= file_byte <= 127):
                # single byte
                continue

            if (194 <= file_byte <= 223):
                # one byte follows
                byte_follow = 1
                continue

            if (224 <= file_byte <= 239):
                # two bytes follow
                byte_follow = 2
                continue

            if (240 <= file_byte <= 244):
                # three bytes follow
                byte_follow = 3
                continue

            # not ASCII or UTF-8
            return False

        # end of file data [byte_follow] must be zero to ensure last character was consumed
        if (byte_follow):
            return False

        # success - return ASCII or UTF-8 result
        return (
            EncodingDetectFile.ENCODING_ASCII
            if (ascii_chars_only)
            else EncodingDetectFile.ENCODING_UTF_8
        )

    def _detect_utf16(self,file_data):
        null_byte_odd,null_byte_even = 0,0
        eol_odd,eol_even = 0,0

        odd_byte = None
        for file_byte in file_data:
            # build pairs of bytes
            if (odd_byte is None):
                odd_byte = file_byte
                continue

            # look for odd/even null byte and check other byte for EOL
            if (odd_byte == 0):
                null_byte_odd += 1
                if (file_byte in EncodingDetectFile.BYTE_EOL):
                    eol_even += 1

            elif (file_byte == 0):
                null_byte_even += 1
                if (odd_byte in EncodingDetectFile.BYTE_EOL):
                    eol_odd += 1

            odd_byte = None

        # attempt detection based on line endings
        if ((not eol_odd) and eol_even):
            return EncodingDetectFile.ENCODING_UTF_16_BE

        if (eol_odd and (not eol_even)):
            return EncodingDetectFile.ENCODING_UTF_16_LE

        # can't detect on line endings - evaluate ratio of null bytes in odd/even positions
        # this will give an indication of how much ASCII (1-127) level text is present
        data_size_half = (len(file_data) / 2)
        threshold_positive = int(data_size_half * EncodingDetectFile.UTF_16_NULL_PERCENT_POSITIVE)
        threshold_negative = int(data_size_half * EncodingDetectFile.UTF_16_NULL_PERCENT_NEGATIVE)

        # must have enough file data to have value ([threshold_positive] must be non-zero)
        if (threshold_positive):
            if ((null_byte_odd > threshold_positive) and (null_byte_even < threshold_negative)):
                return EncodingDetectFile.ENCODING_UTF_16_BE

            if ((null_byte_odd < threshold_negative) and (null_byte_even > threshold_positive)):
                return EncodingDetectFile.ENCODING_UTF_16_LE

        # not UTF-16 - or insufficient data to determine with confidence
        return False

    def load(self,file_path):
        # open file
        fh = open(file_path,'r')

        # detect a byte order mark (BOM)
        file_encoding,bom_marker,file_data = self._detect_bom(fh)
        if (file_encoding):
            # file has a BOM - decode everything past it
            decode = fh.read().decode(file_encoding)
            fh.close()

            return (file_encoding,bom_marker,decode)

        # no BOM - read remaining file data
        file_data.extend(fh.read())
        fh.close()

        # test for ASCII/UTF-8
        file_encoding = self._detect_ascii_utf8(file_data)
        if (file_encoding):
            # file is ASCII or UTF-8 (without BOM)
            return (
                file_encoding,None,
                file_data.decode(file_encoding)
            )

        # test for UTF-16
        file_encoding = self._detect_utf16(file_data)
        if (file_encoding):
            # file is UTF-16(-like) (without BOM)
            return (
                file_encoding,None,
                file_data.decode(file_encoding)
            )

        # can't determine encoding
        return False
