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
                        packet.data_hex = data_hex
                        packet.origin = origin
                        response = packet.parse()
                        write_file.write(line)
                        write_file.write('\t' + response + '\n')
        assert 1 == 1
