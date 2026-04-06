#!/usr/bin/env python3
"""
key_client.py — send a keystroke to key_server.

Usage:
  python key_client.py <host> <port> <event> [long]

Examples:
  python key_client.py localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)"
  python key_client.py localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)" long
"""

import socket
import json
import sys


def send(host, port, event, long=False):
    msg = json.dumps({"event": event, "long": "true" if long else "false"})
    with socket.create_connection((host, port)) as s:
        s.sendall(msg.encode("utf-8"))


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: key_client.py <host> <port> <event> [long]")
        sys.exit(1)
    send(sys.argv[1], int(sys.argv[2]), sys.argv[3], long="long" in sys.argv[4:])
