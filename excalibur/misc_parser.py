import struct
import excalibur.logger as logger


cmd_list = {
    '3906': 'version_number',
    '6f1f': 'heartbeat',
    '711f': 'server_heartbeat_response',
    '6b07': 'login_page_ok',
    '3706': 'server_login_page_ok',
    '2923': 'user_login',
    '2b23': 'server_login_respond',
    'fb09': 'logdata2?',
    '439c': 'user_request_profile?439c',  # not sure about this
    '4406': 'profile_data?4406',
    'e520': 'profile_data?e520',
    'f477': 'profile_data?f477',
    '7868': 'profile_data?7868',
    '9c48': 'profile_data?9c48',
    '499c': 'client_acknowledge?',
}


class Packet:
    """
    this class is meant to be reused by only 1 user
    """

    def get_log_message(self, content):
        self.log.info("[{packet_length}][{unknown}][{cmd}] {content}".format(
            packet_length=self.packet_length,
            unknown=self.unknown,
            cmd=self.cmd,
            content=content
        ))

    def emit_message(self, content):
        self.log.info(self.get_log_message(content))

    def set_packet(self, data, port, origin):
        self.data = data
        self.data_hex = data.hex()
        self.port = port
        self.origin = origin

    # below is all for little endian
    def hex_to_bytes(self, hex_string):
        return bytearray.fromhex(hex_string)

    def __unpack_base(self, format, hex_string):
        temp = struct.unpack_from(format, bytearray.fromhex(hex_string))
        res = temp[0]
        return res

    def hex_to_char(self, hex_string):
        return self.__unpack_base('<c', hex_string)

    def hex_to_short(self, hex_string):
        return self.__unpack_base('<h', hex_string)

    @property
    def cmd(self):
        # if no cmd can be parsed, return just the hex
        cmd_hex = self.data_hex[8:12]
        cmd = cmd_hex

        if cmd_hex in cmd_list:
            cmd = cmd_list[cmd_hex]

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
        return self.data_hex[6:]

    def parse(self):
        try:
            # prints debug raw message
            self.log.debug(self.data_hex)
            # self.log.debug(self.get_log_message(self.data_hex))

            cmd_raw = self.cmd
            self.log.debug('cmd_raw {}'.format(cmd_raw))
            if cmd_raw in cmd_list:
                cmd = cmd_list[cmd_raw]
                if cmd in self.cmd_to_func:
                    func = self.cmd_to_func[cmd]
                    self.log.debug(func)
                    func()
                else:
                    self.parse_unknown()
        except Exception as e:
            self.log.error('{}, failed to parse {}'.format(str(e), self.data_hex))

    def parse_unknown(self):
        self.emit_message("payload")

    def parse_version_number(self):
        version = self.payload()
        self.emit_message("version_number:{version}".format(version=version))

    def parse_heartbeat(self):
        self.emit_message("heartbeat:{self.payload}".format(self.payload))

    def parse_user_credentials(self):
        user_id = self.payload[8:30]  # seems have 8 0 as padding
        password_sha = self.payload[34:98]  # seems have 4 0 as padding
        unknown_part = self.payload[98:]  # ?? this could be time of the login
        self.emit_message("user_id:{user_id} user_password_sha:{password_sha} unknown:{unknown}".format(
            user_id=user_id,
            password_sha=password_sha,
            unknown=unknown_part,
        ))

    def server_login_respond(self):
        user_id = self.payload[8:30]  # seems have 8 0 as padding
        unknown_part = self.payload[34:]  # ?? this could be time of the login
        self.emit_message("user_id:{user_id} unknown:{unknown}".format(
            user_id=user_id,
            unknown=unknown_part,
        ))

    def parse_server_user_login_response(self):
        user_id = self.payload[8:30]  # seems have 8 0 as padding
        unknown_part = self.payload[34:]  # ?? this could be time of the login
        self.emit_message("user_id:{user_id} unknown:{unknown}".format(
            user_id=user_id,
            unknown=unknown_part,
        ))

    def parse_server_heartbeat_response(self):
        self.emit_message("server_heartbeat {}".format(self.payload))

    def parse_login_page_ok(self):
        # [client 45555] 0a00 f003 6b07 0000000001000000 # client sends login page ok message
        self.emit_message("login_page_ok {}".format(self.payload))

    def parse_server_login_page_ok(self):
        # [server 4003] 0a00 f003 3706 8535000001000000 # server reply login page ok?
        self.emit_message("server_login_page_ok {}".format(self.payload))

    def __init__(self, data, port, origin):
        __default_logging_format = '%(asctime)s|%(levelname)s|%(message)s'
        self.log = logger.getlogger(logger_format=__default_logging_format)
        self.data = None
        self.port = None
        self.origin = None
        self.cmd_to_func = {
            'version_number': self.parse_version_number,
            'heartbeat': self.parse_heartbeat,
            'server_heartbeat_response': self.parse_server_heartbeat_response,
            'user_login': self.parse_user_credentials,
            'server_login_respond': self.server_login_respond,
            'login_page_ok': self.parse_login_page_ok,
            'server_login_page_ok': self.parse_server_login_page_ok,
            'logindata2': self.parse_unknown,
        }


__packet_class = None


def parse_packet(data, port, origin):
    """
    use this to parse packet
    """
    global __packet_class
    if not __packet_class:
        __packet_class = Packet(data, port, origin)

    __packet_class.set_packet(data, port, origin)
    return __packet_class.parse()
