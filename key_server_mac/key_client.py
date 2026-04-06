#!/usr/bin/env python3
"""
key_client.py — send one or more keystrokes to key_server over a single connection.

Full input_pipe trigger_input protocol. Each keystroke sends a value 1 (down)
followed by value 0 (up) message. Append :long to simulate a held key.

Usage:
  python key_client.py <host> <port> <event>[;<event>...] [--to TARGET]

event format:  "(EV_KEY), code <N> (<NAME>)"   (value suffix added automatically)
long press:    append :long to the event

Examples:
  python key_client.py localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)"
  python key_client.py localhost 9003 "(EV_KEY), code 28 (KEY_ENTER):long"
  python key_client.py localhost 9003 "(EV_KEY), code 35 (KEY_H);(EV_KEY), code 18 (KEY_E);(EV_KEY), code 38 (KEY_L);(EV_KEY), code 38 (KEY_L);(EV_KEY), code 24 (KEY_O);(EV_KEY), code 28 (KEY_ENTER)"
  python key_client.py localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)" --to keybd1
"""

import socket
import json
import sys


def make_payload(to, events):
    """Build newline-delimited trigger_input messages for all events."""
    lines = []
    for ev_base, long in events:
        down = {"to": to, "event": f"{ev_base}, value 1", "long": "true" if long else "false"}
        up   = {"to": to, "event": f"{ev_base}, value 0", "long": "false"}
        lines.append(f"trigger_input {json.dumps(down)}\n")
        lines.append(f"trigger_input {json.dumps(up)}\n")
    return "".join(lines).encode("utf-8")


def parse_events(raw):
    """Parse ';'-separated event strings. Append :long for a long press."""
    events = []
    for part in raw.split(";"):
        part = part.strip()
        if not part:
            continue
        if part.endswith(":long"):
            events.append((part[:-5].strip(), True))
        else:
            events.append((part, False))
    return events


def send(host, port, to, events):
    payload = make_payload(to, events)
    with socket.create_connection((host, port)) as s:
        s.sendall(payload)


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 3:
        print("usage: key_client.py <host> <port> <event>[;<event>...] [--to TARGET]")
        sys.exit(1)

    host, port, raw = args[0], int(args[1]), args[2]
    to = "keybd1"
    if "--to" in args:
        to = args[args.index("--to") + 1]

    send(host, port, to, parse_events(raw))
