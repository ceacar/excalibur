import socket
import threading
import excalibur
import ctypes
import excalibur.logger as logger
import time


class ProxyBase(threading.Thread):

    def parse_data(self, data, tag):
        try:
            excalibur.proxy_parser.parse(data, self.port, tag)
        except Exception as e:
            print(f'failed to parse data:{data.hex()}, port:{self.port}, tag:{tag}, error: {e}')

    def raise_exception(self):

        # adds ability to raise exception for quitting cmd
        thread_id = ctypes.c_long(self.ident)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class ProxyToServer(ProxyBase):
    def __init__(self, host, port, time_delay=0):
        super(ProxyToServer, self).__init__()
        self.client = None
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))
        self.time_delay = time_delay

    def run(self):
        while True:
            # implement a delay from client, so we can have clear understanding which client traffic triggered a server response
            if self.time_delay > 0:
                time.sleep(self.time_delay)
            # receive from actual server
            data = self.server.recv(4096)
            if data:
                self.parse_data(data, 'server')
                # forward message to client.socket
                self.client.sendall(data)


class ClientToProxy(ProxyBase):
    def __init__(self, host, port, time_delay=0):
        super(ClientToProxy, self).__init__()
        self.server = None
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        self.client, addr = sock.accept()
        self.time_delay = time_delay

    def run(self):
        while True:
            # sends each individual packet with a delay
            if self.time_delay > 0:
                time.sleep(self.time_delay)

            # receive the message from the client
            data = self.client.recv(4096)

            if data:
                self.parse_data(data, 'client')
                # forward to proxy's socket that connects to actual server
                self.server.sendall(data)


class Proxy(ProxyBase):
    def __init__(self, from_host, from_port, to_host, to_port, from_host_time_delay=0, to_host_time_delay=0):
        super(Proxy, self).__init__()
        # from_host from_port is the proxy listening port
        # to_host to_port is the forwarding port of proxy to the actual server
        self.from_host = from_host
        self.to_host = to_host
        try:
            self.from_port = int(from_port)
            self.to_port = int(to_port)
        except ValueError as e:
            print('port has to be a number')
            raise e

        self.client_to_proxy = None
        self.proxy_to_server = None
        self.running = False
        self.client_time_delay = from_host_time_delay
        self.server_time_delay = to_host_time_delay

    def kill(self):
        if self.client_to_proxy:
            self.client_to_proxy.raise_exception()
        if self.proxy_to_server:
            self.proxy_to_server.raise_exception()
        self.raise_exception()

    def get_client_to_proxy_instance(self):
        return ClientToProxy(self.from_host, self.from_port, time_delay=self.client_time_delay)  # point client to my port

    def get_proxy_to_server_instance(self):
        return ProxyToServer(self.to_host, self.to_port, time_delay=self.server_time_delay)

    def run(self):
        while True:
            self.client_to_proxy = self.get_client_to_proxy_instance()
            self.proxy_to_server = self.get_proxy_to_server_instance()
            # give client ability to send data into socket to remote server
            self.client_to_proxy.server = self.proxy_to_server.server
            self.proxy_to_server.client = self.client_to_proxy.client
            self.running = True
            self.client_to_proxy.start()
            self.proxy_to_server.start()


def run_proxy(from_host, from_port, to_host, to_port, from_host_time_delay=0, to_host_time_delay=0):
    __default_logging_format = '%(asctime)s|%(levelname)s|%(message)s'
    log = logger.getlogger(logger_format=__default_logging_format)

    print('Starting Proxy {from_host}:{from_port} -> {to_host}:{to_port}'.format(
        from_host=from_host,
        from_port=from_port,
        to_host=to_host,
        to_port=to_port,
        from_host_time_delay=from_host_time_delay,
        to_host_time_delay=to_host_time_delay,
    ))
    proxy = Proxy(from_host, from_port, to_host, to_port, from_host_time_delay, to_host_time_delay)
    # now starts the proxy server
    proxy.start()

    while True:
        cmd = input('$ ')
        if cmd[:4] == 'quit':
            break
        else:
            log.warning('admin input: {}'.format(cmd))
            if proxy.running:
                cmd_arr = cmd.split()
                if cmd_arr[0].startWith('S'):
                    try:
                        bytes_from_hex = bytearray.fromhex(cmd_arr[1])
                        proxy.proxy_to_server.sendall(bytes_from_hex)
                    except Exception as e:
                        print('error decoding {}, {}'.format(bytes_from_hex, str(e)))

                if cmd_arr[0].startWith('C'):
                    try:
                        bytes_from_hex = bytearray.fromhex(cmd_arr[1])
                        proxy.client_to_proxy.sendall(bytes_from_hex)
                    except Exception as e:
                        print('error decoding {}, {}'.format(bytes_from_hex, str(e)))
    # TODO: added send packets, should i build a queue for it ??

    proxy.kill()
    print('Exiting on cmd {cmd}'.format(cmd=cmd))
    raise Exception('')


if __name__ == '__main__':
    import sys
    _, from_host, from_port, to_host, to_port = sys.argv
    run_proxy(from_host, from_port, to_host, to_port)
