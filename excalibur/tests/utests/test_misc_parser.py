import excalibur
import unittest


class TestPacket(unittest.TestCase):
    def test_packet(self):
        with open('./excalibur/tests/test_data/hex_test_translated', 'w') as write_file:
            with open('./excalibur/tests/test_data/hex_test_data', 'r') as tempf:
                packet = excalibur.misc_parser.Packet()
                for line in tempf:
                    if 'DEBUG' in line:
                        _, _, origin, data_hex = line.rstrip().strip().split('|')
                        packet.set_packet(bytearray.fromhex(data_hex), '1234', origin)
                        response = packet.parse()
                        write_file.write(line)
                        write_file.write('\t' + response + '\n')
        assert 1 == 1

    def test_unpack_as_string_GBK(self):
        chinese_hex = "你好".encode('GBK').hex()
        res = excalibur.hex_utility.unpack_as_string_GBK(chinese_hex)
        actual_output = res[0]
        assert actual_output == "你好"

    # def test_unpack_as_string_utf8(self):
    #     # input_char = '𠾼 𠿪 𡁜 𡁯 𡁵 𡁶 𡁻 𡃁 𡃉 𡇙 𢃇 𢞵 𢫕 𢭃 𢯊 𢱑 𢱕 𢳂 𢴈 𢵌 𢵧 𢺳 𣲷 𤓓 𤶸 𤷪 𥄫 𦉘 𦟌 𦧲 𦧺 𧨾 𨅝 𨈇 𨋢 𨳊 𨳍 𨳒 𩶘'
    #     input_char = '𠾼'
    #     input_hex = input_char.encode('utf-16le').hex()

    #     res = excalibur.hex_utility.unpack_as_string_utf_16le(input_hex)
    #     assert res[0] == '𠾼'
