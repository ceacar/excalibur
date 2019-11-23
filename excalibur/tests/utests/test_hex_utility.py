import unittest
import excalibur


class TestHexUtility(unittest.TestCase):

    def test_unpack_base(self):
        # 'abc' hex code is 616263
        assert excalibur.hex_utility.unpack_as_string('616263') == 'abc'

    def test_auto_unpack_as_int(self):
        assert excalibur.hex_utility.unpack_as_int('21000000') == [33]

    def test_auto_unpack_as_short(self):
        assert excalibur.hex_utility.unpack_as_short('2100') == [33]

    def test_auto_unpack_as_long(self):
        assert excalibur.hex_utility.unpack_as_long('21000000000000') == [33]
