#!/usr/bin/env python

__author__ = "Radoslaw Matusiak"
__copyright__ = "Copyright (c) 2016 Radoslaw Matusiak"
__license__ = "MIT"
__version__ = "0.1"


"""
TCP/UDP proxy.

Modified by @justinc1, to reproduce "EOF occurred in violation of protocol (_ssl.c:997)".
For https://github.com/ScaleComputing/HyperCoreAnsibleCollection,
module certificate.py.
"""

import argparse
import logging
import select
import socket
import time


FORMAT = "%(asctime)-15s %(levelname)-10s %(message)s"
logging.basicConfig(format=FORMAT)
LOGGER = logging.getLogger()


def noop_data_handler(x):
    return x


LOCAL_DATA_HANDLER = noop_data_handler
REMOTE_DATA_HANDLER = noop_data_handler

BUFFER_SIZE = 2**10  # 1024. Keep buffer size as power of 2.


def udp_proxy(src, dst):
    """Run UDP proxy.

    Arguments:
    src -- Source IP address and port string. I.e.: '127.0.0.1:8000'
    dst -- Destination IP address and port. I.e.: '127.0.0.1:8888'
    """
    LOGGER.debug("Starting UDP proxy...")
    LOGGER.debug("Src: {}".format(src))
    LOGGER.debug("Dst: {}".format(dst))

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    proxy_socket.bind(ip_to_tuple(src))

    client_address = None
    server_address = ip_to_tuple(dst)

    LOGGER.debug("Looping proxy (press Ctrl-Break to stop)...")
    while True:
        data, address = proxy_socket.recvfrom(BUFFER_SIZE)

        if client_address is None:
            client_address = address

        if address == client_address:
            data = LOCAL_DATA_HANDLER(data)
            proxy_socket.sendto(data, server_address)
        elif address == server_address:
            data = REMOTE_DATA_HANDLER(data)
            proxy_socket.sendto(data, client_address)
            client_address = None
        else:
            LOGGER.warning("Unknown address: {}".format(str(address)))


# end-of-function udp_proxy


def tcp_proxy(src, dst):
    """Run TCP proxy.

    Arguments:
    src -- Source IP address and port string. I.e.: '127.0.0.1:8000'
    dst -- Destination IP address and port. I.e.: '127.0.0.1:8888'
    """
    LOGGER.debug("Starting TCP proxy...")
    LOGGER.debug("Src: {}".format(src))
    LOGGER.debug("Dst: {}".format(dst))

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(ip_to_tuple(src))
    s.listen(1)

    connection_count = 0
    while 1:
        tcp_proxy_one_conn(s, dst, connection_count)
        connection_count += 1


# end-of-function tcp_proxy


def tcp_proxy_one_conn(s, dst, connection_count):
    s_src, _ = s.accept()
    LOGGER.info(f"New connection from {s_src.getpeername()}")

    s_dst = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s_dst.connect(ip_to_tuple(dst))
    except ConnectionRefusedError:
        # we need to retry.
        # Alternative - forward ConnectionRefusedError to our client,
        # by not listening on src if dest is not available.
        # But how to detect in realtime dest is not available?
        LOGGER.warning(f"ConnectionRefusedError for {dst}, ignore and retry")
        time.sleep(1)
        pass

    sockets = [
        s_src,
        s_dst,
    ]

    restart = False
    while True:
        s_read, _, _ = select.select(sockets, [], [])
        # source = "SRC" if s_read == s_src else "DST"
        # LOGGER.debug('select from {}'.format(source))

        for s in s_read:
            try:
                data = s.recv(BUFFER_SIZE)
            except ConnectionResetError:
                LOGGER.info(f"ConnectionResetError on socket {s}, close and restart")
                restart = True
                break

            if s == s_src:
                d = LOCAL_DATA_HANDLER(data)
                # LOGGER.debug(f'{source} received {len(d)} bytes')
                if len(d) == 0:
                    restart = True
                    break
                try:
                    s_dst.sendall(d)
                except BrokenPipeError:
                    LOGGER.warning(f"BrokenPipeError for {s_dst}, ignore and restart")
                    restart = True
                    break
            elif s == s_dst:
                d = REMOTE_DATA_HANDLER(data)
                # LOGGER.debug(f'{source} received {len(d)} bytes')
                if len(d) == 0:
                    restart = True
                    break
                if inject_ssl_eof_error(connection_count):
                    LOGGER.info(
                        f"Injecting SSL EOF to connection {s_src.getpeername()}"
                    )
                    restart = True
                    break
                s_src.sendall(d)
            # time.sleep(0.1)
        if restart:
            break
    for sock in sockets:
        LOGGER.info(f"Closing connection {sock}")
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError:
            # after BrokenPipeError we want to ignore
            # "OSError: [Errno 107] Transport endpoint is not connected"
            pass
        sock.close()


def inject_ssl_eof_error(connection_count):
    # We want to let 2 connections pass,
    # 3rd - SSL EOF error,
    # then pass
    if connection_count in [2]:
        return True
    return False


def ip_to_tuple(ip):
    """Parse IP string and return (ip, port) tuple.

    Arguments:
    ip -- IP address:port string. I.e.: '127.0.0.1:8000'.
    """
    ip, port = ip.split(":")
    return (ip, int(port))


# end-of-function ip_to_tuple


def main():
    """Main method."""
    parser = argparse.ArgumentParser(description="TCP/UPD proxy.")

    # TCP UPD groups
    proto_group = parser.add_mutually_exclusive_group(required=True)
    proto_group.add_argument("--tcp", action="store_true", help="TCP proxy")
    proto_group.add_argument("--udp", action="store_true", help="UDP proxy")

    parser.add_argument(
        "-s", "--src", required=True, help="Source IP and port, i.e.: 127.0.0.1:8000"
    )
    parser.add_argument(
        "-d",
        "--dst",
        required=True,
        help="Destination IP and port, i.e.: 127.0.0.1:8888",
    )

    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("-q", "--quiet", action="store_true", help="Be quiet")
    output_group.add_argument("-v", "--verbose", action="store_true", help="Be loud")

    args = parser.parse_args()

    if args.quiet:
        LOGGER.setLevel(logging.CRITICAL)
    if args.verbose:
        LOGGER.setLevel(logging.NOTSET)

    if args.udp:
        udp_proxy(args.src, args.dst)
    elif args.tcp:
        tcp_proxy(args.src, args.dst)


# end-of-function main


if __name__ == "__main__":
    main()
