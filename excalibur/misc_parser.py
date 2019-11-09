import struct
import excalibur.logger as logger
import excalibur


class Packet:
    """
    this class is meant to be reused by only 1 user
    """

    def get_log_message(self, content):
        """
        use <- to indicated receving from client
        use -> to indicate sending to client
        """
        origin_tag = " <- "

        if self.origin == "server":
            origin_tag = " -> "

        cmd_adjusted = "{cmd}:{raw_cmd}".format(
            cmd=self.cmd,
            raw_cmd=self.raw_cmd,
        ).ljust(25, '-')  # ljust to align output

        cmd_string = '[{}]'.format(cmd_adjusted)

        return "{origin}[{packet_length}][{unknown}]{cmd} {content}".format(
            packet_length=self.packet_length,
            origin=origin_tag,
            unknown=self.unknown,
            cmd=cmd_string,
            content=content
        )

    def emit_message(self, content):
        msg = self.get_log_message(content)
        self.log.info(msg)
        return msg

    def set_packet(self, data, port, origin):
        self.data = data
        self.data_hex = data.hex()
        self.port = port
        self.origin = origin

    # below is all for little endian
    def hex_to_bytes(self, hex_string):
        return bytearray.fromhex(hex_string)

    def __unpack_base(self, format, hex_string):
        res = struct.unpack_from(format, bytearray.fromhex(hex_string))
        return res

    def unpack_string(self, format, hex_string, decoder="utf-8"):
        res = self.__unpack_base(format, hex_string)
        decoded_arr = [unpacked.decode(decoder) for unpacked in res]
        str_output = ''.join(d if d != '\x00' else '' for d in decoded_arr)  # \x00 means null
        return str_output

    def auto_unpack_as_string(self, hex_string, decoder="utf-8"):
        format = '<' + 's' * int(len(hex_string) / 2)
        return self.unpack_string(format, hex_string, decoder)

    def hex_to_char(self, hex_string):
        return self.__unpack_base('<c', hex_string)[0]

    def hex_to_short(self, hex_string):
        return self.__unpack_base('<h', hex_string)[0]

    def auto_unpack_as_int(self, hex_string):
        format = '<' + 'i' * int(len(hex_string) / 8)
        return self.__unpack_base(format, hex_string)

    def auto_unpack_as_short(self, hex_string):
        format = '<' + 'h' * int(len(hex_string) / 4)
        return self.__unpack_base(format, hex_string)

    @property
    def raw_cmd(self):
        return self.data_hex[8:12]

    @property
    def cmd(self):
        # if no cmd can be parsed, return just the hex
        cmd_hex = self.raw_cmd
        cmd = '????'

        if cmd_hex in self.cmd_list:
            cmd = self.cmd_list[cmd_hex]

        return cmd

    @property
    def unknown(self):
        unknown_hex = self.data_hex[4:8]
        return unknown_hex

    @property
    def packet_length(self):
        packet_length_hex = self.data_hex[:4]
        # is this unknown alway 03f0??(short is 1008)
        packet_length = self.hex_to_short(packet_length_hex)
        return packet_length

    @property
    def length(self):
        """
        returns actual length of data the packet carries
        it is length of packet - length of (packet_length + uknown + cmd)
        which is 6
        so it is self.packet_length -6
        """
        return self.packet_length - 6

    @property
    def payload(self):
        return self.data_hex[12:]

    def parse(self):
        try:
            self.log.debug(self.origin + '|' + self.data_hex)
            cmd = self.cmd
            # self.log.debug('cmd_raw {}'.format(cmd_raw))
            if cmd in self.cmd_to_func:
                func = self.cmd_to_func[cmd]
                return func()
            else:
                return self.parse_unknown()
        except Exception as e:
            self.log.error('{}, failed to parse {}'.format(str(e), self.data_hex))

    def parse_unknown(self):
        msg = self.payload
        return self.emit_message(msg)

    def parse_version_number(self):
        version = self.payload
        msg = "version_number:{version}".format(version=version)
        return self.emit_message(msg)

    def parse_heartbeat(self):
        msg = self.payload
        return self.emit_message(msg)

    def parse_user_credentials(self):
        user_id = self.payload[8:30]  # seems have 8 0 as padding
        password_sha = self.payload[34:98]  # seems have 4 0 as padding
        unknown_part = self.payload[98:]  # ?? this could be time of the login
        msg = "user_id:{user_id} user_password_sha:{password_sha} unknown:{unknown}".format(
            user_id=user_id,
            password_sha=password_sha,
            unknown=unknown_part,
        )
        return self.emit_message(msg)

    def server_login_respond(self):
        user_id = self.payload[8:30]  # seems have 8 0 as padding
        unknown_part = self.payload[34:]  # ?? this could be time of the login
        msg = "user_id:{user_id} unknown:{unknown}".format(
            user_id=user_id,
            unknown=unknown_part,
        )
        return self.emit_message(msg)

    def parse_server_user_login_response(self):
        user_id = self.payload[8:30]  # seems have 8 0 as padding
        unknown_part = self.payload[34:]  # ?? this could be time of the login
        msg = "user_id:{user_id} unknown:{unknown}".format(
            user_id=user_id,
            unknown=unknown_part,
        )
        return self.emit_message(msg)

    def parse_server_heartbeat_response(self):
        msg = self.payload
        return self.emit_message(msg)

    def parse_login_page_ok(self):
        # [client 45555] 0a00 f003 6b07 0000000001000000 # client sends login page ok message
        msg = self.payload
        return self.emit_message(msg)

    def parse_server_login_page_ok(self):
        # [server 4003] 0a00 f003 3706 8535000001000000 # server reply login page ok?
        msg = "{}".format(self.payload)
        return self.emit_message(msg)

    def parse_user_info(self):
        # user_name_length = self.__unpack_base('<h', self.payload[4:6])  # 08 means name is 8 bytes long?
        uuid = self.payload[:6]
        user_name_hex = self.payload[6:38]  # 16 bytes is name  data_hex[16:50]
        user_name = self.unpack_string('<ssssssssssssssss', user_name_hex)
        rank_exp_hex = self.data_hex[136:144]
        rank_exp = self.auto_unpack_as_int(rank_exp_hex)

        msg = "uuid:[{uuid}], user_name:{user_name}, rank_exp:{rank_exp}".format(
            uuid=uuid,
            user_name=user_name,
            rank_exp=rank_exp,
            # length=user_name_length
        )
        # TODO: unfinished

        return self.emit_message(msg)

    def parse_data_packet(self):
        if self.packet_length == 1702 and self.unknown == '8535' and self.raw_cmd == '0000':
            # this is a user info packet
            return self.parse_user_info()
        else:
            return self.parse_unknown()

    def parse_timestamp(self):
        import pdb
        pdb.set_trace()
        timestamp_hex = self.payload[33:41]
        unpack_temp = self.auto_unpack_as_int(timestamp_hex)
        timestamp_unix_time = unpack_temp[0]
        dt = excalibur.time_conversion.from_unix(timestamp_unix_time)
        self.emit_message("timestamp:{}, payload:{}".format(dt, self.payload))

    def __init__(self):
        __default_logging_format = '%(asctime)s|%(levelname)s|%(message)s'
        # __default_logging_format = '%(message)s'
        self.log = logger.getlogger(logger_format=__default_logging_format)
        self.data = None
        self.port = None
        self.origin = None

        self.cmd_list = {
            '3906': 'version_number',
            '6f1f': 'heartbeat',
            '711f': 'server_heartbeat_response',
            '6b07': 'login_page_ok',
            '3706': 'server_login_page_ok',
            '2923': 'user_login',
            '2b23': 'server_login_respond',
            'fb09': 'logdata2?',
            '439c': 'log_data4?439c',  # not sure about this
            '4406': 'profile_data?',
            'e520': 'profile_data?',
            'f477': 'profile_data?',
            '7868': 'profile_data?',
            '9c48': 'profile_data?',
            '499c': 'client_acknowledge?',
            '4d0a': 'ip_with_port?',  # x.x.x.x:xxxx
            '4f05': 'internal_ip_port?',
            '4708': 'timestamp_or_udp_ip_port?',
            '2f23': 'timestamp_or_udp_response',  # did server timestamp the client ack profile
            '4007': 'request_garage_page',
            '8535': 'user_info',
            '0000': 'data_transfer',
            'e807': 'client_ack_profile',
            '2207': '2f23_cli_ack',
            '350a': 'user_key_bind_cli_req',
            '0109': 'srv_send_user_key_bind',
            '2e0a': 'unknown_request',
            '3e08': 'friend_list_req_related',
            '2000': 'unknown_request',
            '2c06': 'change_of_keybind',
            '8e06': 'logout??',
            '6806': 'garage_1st_page',
            '3c07': 'garage_page_count',
            '0621': 'gasha??',
            '5a09': 'traing_ground_garage_req',
            '5807': 'friend_search',
            '6008': 'time_sync_req?',
            'd30a': 'battle_heart_beat',
            '5607': 'gasha_draw?',
            '1e07': 'mb_draw',
            'b005': 'gp_draw',
            '1708': 'custom_draw',
            '0c06': 'set_battle_suit',
        }

        self.cmd_to_func = {
            'version_number': self.parse_version_number,
            'heartbeat': self.parse_heartbeat,
            'server_heartbeat_response': self.parse_server_heartbeat_response,
            'user_login': self.parse_user_credentials,
            'server_login_respond': self.server_login_respond,
            'login_page_ok': self.parse_login_page_ok,
            'server_login_page_ok': self.parse_server_login_page_ok,
            'logindata2': self.parse_unknown,
            'user_info': self.parse_user_info,
            'data_transfer': self.parse_data_packet,
            'client_ack_profile': self.parse_unknown,
            # 'timestamp_or_udp_response': self.parse_timestamp,  # did server timestamp the client ack profile
        }


__packet_class = None


def parse_packet(data, port, origin):
    """
    use this to parse packet
    """
    global __packet_class
    if not __packet_class:
        __packet_class = Packet()

    __packet_class.set_packet(data, port, origin)
    __packet_class.parse()
