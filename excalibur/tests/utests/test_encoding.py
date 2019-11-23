import excalibur
import unittest


class TestEncoding(unittest.TestCase):
    def test_check_utf_8_length(self):
        input_char = '我'
        # 'e68891'
        input_hex = input_char.encode('utf-8').hex()
        assert excalibur.encoding.check_utf8_length(input_hex) == 3

    def test_decode_utf8_with_auto_length_detection(self):
        hex_input = '我'.encode('utf-8').hex()
        # 'e68891'
        res = excalibur.encoding.decode_utf8_with_auto_length_detection(hex_input)
        assert res == '我'

        hex_input = '我无敌寂寞'.encode('utf-8').hex()
        # 'e68891'
        res = excalibur.encoding.decode_utf8_with_auto_length_detection(hex_input)
        assert res == '我无敌寂寞'

        hex_input = 'e68891ffe697a0'
        res = excalibur.encoding.decode_utf8_with_auto_length_detection(hex_input)
        assert res == '我?无'


    def test_check_utf16_length(self):
        hex_input = '我'.encode('utf-16').hex()
        # 'fffe 1162'
        assert excalibur.encoding.check_utf16_length(hex_input) == 2 + 2  # 2 is the actual length and another 2 is for the BOM

        # 'fffe43d8bcdf'
        hex_input = '𠾼'.encode('utf-16').hex()
        assert excalibur.encoding.check_utf16_length(hex_input) == 6

        hex_input = 'fffffffe43d8bcdf'  # should only checks for first ffff(2 byte)
        assert excalibur.encoding.check_utf16_length(hex_input) == 2

    def test_decode_utf16_with_auto_length_detection(self):
        hex_input = '我'.encode('utf-16').hex()
        # 'fffe 1162'
        assert excalibur.encoding.decode_utf16_with_auto_length_detection(hex_input) == '我'

        hex_input= '𠾼'.encode('utf-16').hex()
        # 'fffe43d8bcdf'
        assert excalibur.encoding.decode_utf16_with_auto_length_detection(hex_input) == '𠾼'

        # broken 00 hex in middle
        hex_input = '116200fffe43d8bcdf'
        # this is messed up decode
        assert excalibur.encoding.decode_utf16_with_auto_length_detection(hex_input) ==  '我＀䏾볘?'
