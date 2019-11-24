import excalibur.logger as logger
import excalibur
import os


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

    def get_next_package(self):
        # server sometimes will chain message together, so need to loop through them and parse one by one
        length = self.next_packet_length
        end = 8 + length * 2
        self.data_hex = self.data_hex_cache[0:end]  # first 4 bytes are length + f003
        self.data_hex_cache = self.data_hex_cache[end:]  # remove this package from self.data_hex_cache for next package split
        return self.data_hex

    def emit_message(self, content):
        msg = self.get_log_message(content)
        self.log.info(msg)
        return msg

    def set_packet(self, data, port, origin):
        self.data = data
        self.data_hex_all = data.hex()
        self.data_hex_cache = self.data_hex_all  # cache used to help get split chained packages
        self.get_next_package()  # self.data_hex is used as temporary placeholder for one packet
        self.port = port
        self.origin = origin

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
        packet_length = excalibur.hex_utility.unpack_as_short(packet_length_hex)
        return packet_length[0]

    @property
    def next_packet_length(self):
        if self.data_hex_cache:
            packet_length_hex = self.data_hex_cache[:4]
            # is this unknown alway 03f0??(short is 1008)
            packet_length = excalibur.hex_utility.unpack_as_short(packet_length_hex)
            return packet_length[0]
        return 0

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
        res = []
        while self.data_hex:
            try:
                self.log.debug(self.origin + '|' + self.data_hex)
                cmd = self.cmd
                # self.log.debug('cmd_raw {}'.format(cmd_raw))
                if cmd in self.cmd_to_func:
                    func = self.cmd_to_func[cmd]
                    res.append(func())
                else:
                    res.append(self.parse_unknown())
            except Exception as e:
                self.log.error('{}, failed to parse {}'.format(str(e), self.data_hex))
                res.append(str(e))

            if self.next_packet_length <= 0:
                # no more packet
                self.data_hex = ""
            else:
                self.get_next_package()

        return '\n\t'.join(res)

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
        user_id = excalibur.hex_utility.unpack_as_string(self.payload[8:30])  # seems have 8 0 as padding
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

    def parse_user_menu_action_req(self):
        # [client 45555] 0a00 f003 6b07 0000000001000000 # client sends login page ok message
        # 11th byte is the action type
        action_hex = self.payload[8:10]

        if action_hex in self.user_action_type:
            action_type = self.user_action_type[action_hex]
        else:
            action_type = "????"

        msg = "user_request:{typ}; {payload}".format(
            typ=action_type,
            payload=self.payload
        )
        return self.emit_message(msg)

    def parse_server_user_menu_action_req(self):
        action_hex = self.payload[8:10]

        if action_hex in self.user_action_type:
            action_type = self.user_action_type[action_hex]
        else:
            action_type = "????"

        msg = "srv_respond:{typ} ok; {payload}".format(
            typ=action_type,
            payload=self.payload
        )
        return self.emit_message(msg)

    def parse_user_info(self):
        # user_name_length = self.__unpack_base('<h', self.payload[4:6])  # 08 means name is 8 bytes long?
        uuid = self.payload[:6]
        user_name_hex = self.payload[6:38]  # 16 bytes is name  data_hex[16:50]
        user_name = excalibur.hex_utility.unpack_as_string(user_name_hex)
        rank_exp_hex = self.data_hex[136:144]
        rank_exp = excalibur.hex_utility.unpack_as_int(rank_exp_hex)

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
        unpack_temp = excalibur.hex_utility.unpack_as_int(timestamp_hex)
        timestamp_unix_time = unpack_temp[0]
        dt = excalibur.time_conversion.from_unix(timestamp_unix_time)
        return self.emit_message("timestamp:{}, payload:{}".format(dt, self.payload))

    def parse_server_info_request(self):
        server_code = self.payload[-8:-4]
        return self.emit_message('requested server:{}, {}'.format(server_code, self.payload))

    def parse_respond_server_info(self):
        # 000000008e23682423000000
        server_info_hex = self.payload[9:19]
        res = excalibur.hex_utility.unpack_as_decimal_list(server_info_hex)
        return self.emit_message('server: {}'.format('.'.join([str(temp) for temp in res])))

    def parse_respond_time_sync_request(self):
        # 1600 f003 2c07 85350000 e307(year: 2019) 0100(month: 01) 0d00(day: 13) 1400(hour:20) 0500(minute:05) 1e00(second:30) 0b01(milisecond:267) 0000
        year_hex = self.payload[8:12]
        month_hex = self.payload[12:16]
        day_hex = self.payload[16:20]
        hour_hex = self.payload[20:24]
        minute_hex = self.payload[20:24]
        second_hex = self.payload[24:28]
        millisecond_hex = self.payload[28:32]
        microsecond_hex = self.payload[32:36]

        year = excalibur.hex_utility.unpack_as_short(year_hex)[0]
        month = excalibur.hex_utility.unpack_as_short(month_hex)[0]
        day = excalibur.hex_utility.unpack_as_short(day_hex)[0]
        hour = excalibur.hex_utility.unpack_as_short(hour_hex)[0]
        minute = excalibur.hex_utility.unpack_as_short(minute_hex)[0]
        second = excalibur.hex_utility.unpack_as_short(second_hex)[0]
        millisecond = excalibur.hex_utility.unpack_as_short(millisecond_hex)[0]
        microsecond = excalibur.hex_utility.unpack_as_short(microsecond_hex)[0]

        return self.emit_message('{y}-{m}-{d} {H}:{M}:{s}.{S}; {payload}'.format(
            y=year,
            m=month,
            d=day,
            H=hour,
            M=minute,
            s=second,
            S=str(millisecond).rjust(3, '0') + str(microsecond).rjust(3, '0'),
            payload=self.payload[36:],
        ))

    def parse_respond_time_2(self):
        year_hex = self.payload[8:12]
        month_hex = self.payload[12:16]
        day_hex = self.payload[16:20]
        hour_hex = self.payload[20:24]

        year = excalibur.hex_utility.unpack_as_short(year_hex)[0]
        month = excalibur.hex_utility.unpack_as_short(month_hex)[0]
        day = excalibur.hex_utility.unpack_as_short(day_hex)[0]
        hour = excalibur.hex_utility.unpack_as_short(hour_hex)[0]

        return self.emit_message('{y}-{m}-{d} {H}; {payload}'.format(
            y=year,
            m=month,
            d=day,
            H=hour,
            payload=self.payload[24:],
        ))


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
            '6b07': 'user_menu_action_req',
            '3706': 'srv_user_menu_action_rsp',
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
            '4708': 'request_server_info',
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
            'ad07': 'respond_server_info',
            '2c07': 'respond_time_sync_req',
            'ee08': 'respond_time_2',
            '5a05': '5a05_login_last_msg',
        }

        self.cmd_to_func = {
            'version_number': self.parse_version_number,
            'heartbeat': self.parse_heartbeat,
            'server_heartbeat_response': self.parse_server_heartbeat_response,
            'user_login': self.parse_user_credentials,
            'server_login_respond': self.server_login_respond,
            'user_menu_action_req': self.parse_user_menu_action_req,
            'srv_user_menu_action_rsp': self.parse_server_user_menu_action_req,
            'logindata2': self.parse_unknown,
            'user_info': self.parse_user_info,
            'data_transfer': self.parse_data_packet,
            'client_ack_profile': self.parse_unknown,
            'request_server_info': self.parse_server_info_request,  # did server timestamp the client ack profile
            'respond_server_info': self.parse_respond_server_info,  # server responds with server info
            'respond_time_sync_req': self.parse_respond_time_sync_request,
            'respond_time_2': self.parse_respond_time_2,
        }

        self.user_action_type = {
            "01": "login_page",
            "02": "my_room",
            "03": "mission_channel",
            "07": "gasha",
            "0c": "medal",
            "0a": "logout",
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


def parse_log(log_path):
    log_path = os.path.expanduser(log_path)
    with open(log_path, 'r') as tempf:
        packet = Packet()
        __default_logging_format = '%(asctime)s|%(levelname)s|%(message)s'
        # write log to file
        packet.log = logger.get_file_logger(
            log_file_path=log_path+'.translated', logger_format=__default_logging_format)

        for line in tempf:
            if 'DEBUG' in line:
                _, _, origin, data_hex = line.rstrip().strip().split('|')
                packet.set_packet(bytearray.fromhex(data_hex), '1234', origin)
                response = packet.parse()
