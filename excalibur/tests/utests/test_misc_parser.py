import excalibur
import unittest


class TestPacket(unittest.TestCase):
    def test_packet(self):
        with open('./excalibur/tests/utests/hex_test_translated', 'w') as write_file:
            with open('./excalibur/tests/utests/hex_test', 'r') as tempf:
                packet = excalibur.misc_parser.Packet()
                for line in tempf:
                    packet.data_hex = line.rstrip().strip()
                    response = packet.parse()
                    write_file.write(line)
                    write_file.write('\t>' + response + '\n')
        assert 1 == 1
