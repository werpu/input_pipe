#!/usr/bin/env python3
"""
key_server.py — minimal TCP keyboard injection server for macOS.

Protocol (same as Linux key_server):
  {"event": "(EV_KEY), code 28 (KEY_ENTER)"}
  {"event": "(EV_KEY), code 28 (KEY_ENTER)", "long": "true"}

"to" is accepted but ignored.

Usage:
  python key_server.py          # listens on default port 9003
  python key_server.py -p 9002  # custom port

Requires Accessibility permission:
  System Preferences → Security & Privacy → Accessibility
"""

import asyncio
import json
import argparse
from pynput.keyboard import Controller, Key, KeyCode

DELAY = 50e-3  # seconds between press/release and long-press repeats

keyboard = Controller()

# Map Linux KEY_* names to pynput Key or single characters
KEY_MAP = {
    "KEY_ENTER":      Key.enter,
    "KEY_ESC":        Key.esc,
    "KEY_SPACE":      Key.space,
    "KEY_BACKSPACE":  Key.backspace,
    "KEY_TAB":        Key.tab,
    "KEY_DELETE":     Key.delete,
    "KEY_HOME":       Key.home,
    "KEY_END":        Key.end,
    "KEY_PAGEUP":     Key.page_up,
    "KEY_PAGEDOWN":   Key.page_down,
    "KEY_UP":         Key.up,
    "KEY_DOWN":       Key.down,
    "KEY_LEFT":       Key.left,
    "KEY_RIGHT":      Key.right,
    "KEY_LEFTSHIFT":  Key.shift,
    "KEY_RIGHTSHIFT": Key.shift_r,
    "KEY_LEFTCTRL":   Key.ctrl,
    "KEY_RIGHTCTRL":  Key.ctrl_r,
    "KEY_LEFTALT":    Key.alt,
    "KEY_RIGHTALT":   Key.alt_r,
    "KEY_LEFTMETA":   Key.cmd,
    "KEY_RIGHTMETA":  Key.cmd_r,
    "KEY_CAPSLOCK":   Key.caps_lock,
    "KEY_F1":  Key.f1,  "KEY_F2":  Key.f2,  "KEY_F3":  Key.f3,
    "KEY_F4":  Key.f4,  "KEY_F5":  Key.f5,  "KEY_F6":  Key.f6,
    "KEY_F7":  Key.f7,  "KEY_F8":  Key.f8,  "KEY_F9":  Key.f9,
    "KEY_F10": Key.f10, "KEY_F11": Key.f11, "KEY_F12": Key.f12,
    # alphanumeric — resolved dynamically below
}

# Resolve KEY_A–KEY_Z and KEY_0–KEY_9 dynamically
for _c in "abcdefghijklmnopqrstuvwxyz":
    KEY_MAP[f"KEY_{_c.upper()}"] = KeyCode.from_char(_c)
for _d in "0123456789":
    KEY_MAP[f"KEY_{_d}"] = KeyCode.from_char(_d)


def parse_event(ev_str):
    """'(EV_KEY), code 28 (KEY_ENTER)' → pynput key"""
    parts = [s.strip() for s in ev_str.split(",")]
    key_name = parts[1].split()[2][1:-1]   # "code 28 (KEY_ENTER)" → "KEY_ENTER"
    key = KEY_MAP.get(key_name)
    if key is None:
        raise ValueError(f"unknown key: {key_name}")
    return key


async def press(key, long=False):
    keyboard.press(key)
    if long:
        for _ in range(10):
            await asyncio.sleep(DELAY)
            keyboard.press(key)
    await asyncio.sleep(DELAY)
    keyboard.release(key)


async def handle(reader, writer):
    try:
        data = await reader.read(4096)
        msg = json.loads(data.decode("utf-8").strip())
        key = parse_event(msg["event"])
        await press(key, long=str(msg.get("long", "false")).lower() == "true")
    except Exception as e:
        print(f"error: {e}")
    finally:
        writer.close()


async def main(port):
    print(f"listening on port {port}")
    server = await asyncio.start_server(handle, host=None, port=port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--port", type=int, default=9003)
    asyncio.run(main(**vars(p.parse_args())))
