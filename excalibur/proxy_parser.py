"""
proxy_parser.py is providing parser for proxy.Proxy
"""


def parse(data, port, origin):
    print("[{origin} {port}] {data}".format(
        origin=origin,
        port=port,
        data=data.hex(),
    ))
