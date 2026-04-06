#!/usr/bin/env python3
"""
key_server.py — minimal TCP keyboard injection server for macOS.

Full input_pipe trigger_input protocol:
  trigger_input {"to": "keybd1", "event": "(EV_KEY), code 28 (KEY_ENTER), value 1", "long": "false"}
  trigger_input {"to": "keybd1", "event": "(EV_KEY), code 28 (KEY_ENTER), value 0", "long": "false"}

"to" is accepted but ignored — there is only one virtual keyboard device.
value 1 = key down, value 0 = key up, value 2 = repeat.
Omitting value performs a full press+release in one message (legacy).

Multiple newline-terminated messages may be sent on a single connection.

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
    """
    '(EV_KEY), code 28 (KEY_ENTER), value 1' → (pynput_key, value_or_None)
    value is None when the ', value N' suffix is absent.
    """
    parts = [s.strip() for s in ev_str.split(",")]
    key_name = parts[1].split()[2][1:-1]   # "code 28 (KEY_ENTER)" → "KEY_ENTER"
    key = KEY_MAP.get(key_name)
    if key is None:
        raise ValueError(f"unknown key: {key_name}")
    value = None
    if len(parts) >= 3 and parts[2].startswith("value"):
        value = int(parts[2].split()[1])
    return key, value


async def press(key, value, long=False):
    if value == 1:
        keyboard.press(key)
        if long:
            for _ in range(10):
                await asyncio.sleep(DELAY)
                keyboard.press(key)
    elif value == 0:
        keyboard.release(key)
    elif value == 2:
        keyboard.press(key)   # repeat
    else:
        # legacy: no value → full press+release
        keyboard.press(key)
        if long:
            for _ in range(10):
                await asyncio.sleep(DELAY)
                keyboard.press(key)
        await asyncio.sleep(DELAY)
        keyboard.release(key)


async def handle(reader, writer):
    try:
        while True:
            line = await reader.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue
            text = line.decode("utf-8")
            if text.startswith("trigger_input "):
                text = text[len("trigger_input "):]
            msg = json.loads(text)
            key, value = parse_event(msg["event"])
            await press(key, value, long=str(msg.get("long", "false")).lower() == "true")
    except Exception as e:
        print(f"error: {e}")
    finally:
        writer.close()


async def main(port):
    print(f"listening on port {port}")
    server = await asyncio.start_server(handle, host="0.0.0.0", port=port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--port", type=int, default=9003)
    asyncio.run(main(**vars(p.parse_args())))
