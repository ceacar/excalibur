import socket
import threading
import excalibur
import ctypes
import excalibur.logger as logger


__default_logging_format = '%(asctime)s|%(levelname)s|%(message)s'
log = logger.getlogger(logger_format=__default_logging_format)


class ProxyBase(threading.Thread):

    def parse_data(self, data, tag):
        excalibur.proxy_parser.parse(data, self.port, tag)

    def raise_exception(self):
        # adds ability to raise exception for quitting cmd
        thread_id = ctypes.c_long(self.ident)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class ProxyToServer(ProxyBase):
    def __init__(self, host, port):
        super(ProxyToServer, self).__init__()
        self.client = None
        self.port = port
        self.host = host
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    def run(self):
        while True:
            # receive from actual server
            data = self.server.recv(4096)
            self.parse_data(data, 'server')
            if data:
                # forward message to client.socket
                self.client.sendall(data)


class ClientToProxy(ProxyBase):
    def __init__(self, host, port):
        super(ClientToProxy, self).__init__()
        self.server = None
        self.port = port
        self.host = host
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)
        self.client, addr = sock.accept()

    def run(self):
        while True:
            # receive the message from the client
            data = self.client.recv(4096)
            if data:
                self.parse_data(data, 'client')
                # forward to proxy's socket that connects to actual server
                self.server.sendall(data)


class Proxy(ProxyBase):
    def __init__(self, from_host, from_port, to_host, to_port):
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

    def kill(self):
        if self.client_to_proxy:
            self.client_to_proxy.raise_exception()
        if self.proxy_to_server:
            self.proxy_to_server.raise_exception()
        self.raise_exception()

    def run(self):
        while True:
            self.client_to_proxy = ClientToProxy(self.from_host, self.from_port)  # point client to my port
            self.proxy_to_server = ProxyToServer(self.to_host, self.to_port)
            # give client ability to send data into socket to remote server
            self.client_to_proxy.server = self.proxy_to_server.server
            self.proxy_to_server.client = self.client_to_proxy.client
            self.proxy_to_server.daemon = True

            self.client_to_proxy.start()
            self.proxy_to_server.start()


def run_proxy(from_host, from_port, to_host, to_port):
    print('Starting Proxy {from_host}:{from_port} -> {to_host}:{to_port}'.format(
        from_host=from_host,
        from_port=from_port,
        to_host=to_host,
        to_port=to_port,
    ))
    proxy = Proxy(from_host, from_port, to_host, to_port)
    # now starts the proxy server
    proxy.start()

    while True:
        cmd = input('$ ')
        if cmd[:4] == 'quit':
            break
        else:
            log.warning('admin input: {}'.format(cmd))

    proxy.kill()
    print('Exiting on cmd {cmd}'.format(cmd=cmd))
    raise Exception('')


if __name__ == '__main__':
    import sys
    _, from_host, from_port, to_host, to_port = sys.argv
    run_proxy(from_host, from_port, to_host, to_port)
