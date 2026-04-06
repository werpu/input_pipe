#!/usr/bin/env python3
"""
key_server.py — minimal TCP keyboard injection server.

Protocol (same as input_pipe trigger_input):
  {"event": "(EV_KEY), code 28 (KEY_ENTER)"}
  {"event": "(EV_KEY), code 28 (KEY_ENTER)", "long": "true"}

"to" is accepted but ignored — there is only one virtual keyboard device.

Usage:
  python key_server.py          # listens on default port 9003
  python key_server.py -p 9002  # custom port
"""

import asyncio
import json
import argparse
from evdev import UInput, ecodes

DELAY = 50e-3  # seconds between press/release and long-press repeats

CAPS = {
    ecodes.EV_KEY: [
        ecodes.KEY_0, ecodes.KEY_1, ecodes.KEY_2, ecodes.KEY_3, ecodes.KEY_4,
        ecodes.KEY_5, ecodes.KEY_6, ecodes.KEY_7, ecodes.KEY_8, ecodes.KEY_9,
        ecodes.KEY_A, ecodes.KEY_B, ecodes.KEY_C, ecodes.KEY_D, ecodes.KEY_E,
        ecodes.KEY_F, ecodes.KEY_G, ecodes.KEY_H, ecodes.KEY_I, ecodes.KEY_J,
        ecodes.KEY_K, ecodes.KEY_L, ecodes.KEY_M, ecodes.KEY_N, ecodes.KEY_O,
        ecodes.KEY_P, ecodes.KEY_Q, ecodes.KEY_R, ecodes.KEY_S, ecodes.KEY_T,
        ecodes.KEY_U, ecodes.KEY_V, ecodes.KEY_W, ecodes.KEY_X, ecodes.KEY_Y,
        ecodes.KEY_Z,
        ecodes.KEY_F1,  ecodes.KEY_F2,  ecodes.KEY_F3,  ecodes.KEY_F4,
        ecodes.KEY_F5,  ecodes.KEY_F6,  ecodes.KEY_F7,  ecodes.KEY_F8,
        ecodes.KEY_F9,  ecodes.KEY_F10, ecodes.KEY_F11, ecodes.KEY_F12,
        ecodes.KEY_UP, ecodes.KEY_DOWN, ecodes.KEY_LEFT, ecodes.KEY_RIGHT,
        ecodes.KEY_ENTER, ecodes.KEY_SPACE, ecodes.KEY_BACKSPACE, ecodes.KEY_ESC,
        ecodes.KEY_TAB, ecodes.KEY_DELETE, ecodes.KEY_HOME, ecodes.KEY_END,
        ecodes.KEY_PAGEUP, ecodes.KEY_PAGEDOWN,
        ecodes.KEY_LEFTSHIFT, ecodes.KEY_RIGHTSHIFT,
        ecodes.KEY_LEFTCTRL, ecodes.KEY_RIGHTCTRL,
        ecodes.KEY_LEFTALT, ecodes.KEY_RIGHTALT,
        ecodes.KEY_LEFTMETA, ecodes.KEY_RIGHTMETA,
        ecodes.KEY_CAPSLOCK, ecodes.KEY_MINUS, ecodes.KEY_EQUAL,
        ecodes.KEY_COMMA, ecodes.KEY_DOT, ecodes.KEY_SLASH, ecodes.KEY_SEMICOLON,
        ecodes.KEY_KP0, ecodes.KEY_KP1, ecodes.KEY_KP2, ecodes.KEY_KP3,
        ecodes.KEY_KP4, ecodes.KEY_KP5, ecodes.KEY_KP6, ecodes.KEY_KP7,
        ecodes.KEY_KP8, ecodes.KEY_KP9, ecodes.KEY_KPENTER, ecodes.KEY_KPPLUS,
        ecodes.KEY_KPMINUS, ecodes.KEY_KPASTERISK, ecodes.KEY_KPDOT,
    ]
}


def parse_event(ev_str):
    """'(EV_KEY), code 28 (KEY_ENTER)' → (ev_type_int, ev_code_int)"""
    parts = [s.strip() for s in ev_str.split(",")]
    ev_type = getattr(ecodes, parts[0][1:-1])   # strip parens → EV_KEY
    ev_code = int(parts[1].split()[1])           # "code 28 (KEY_ENTER)" → 28
    return ev_type, ev_code


async def press(ui, ev_type, ev_code, long=False):
    ui.write(ev_type, ev_code, 1)
    ui.syn()
    if long:
        for _ in range(10):
            await asyncio.sleep(DELAY)
            ui.write(ev_type, ev_code, 2)
            ui.syn()
    await asyncio.sleep(DELAY)
    ui.write(ev_type, ev_code, 0)
    ui.syn()


async def handle(reader, writer, ui):
    try:
        data = await reader.read(4096)
        msg = json.loads(data.decode("utf-8").strip())
        ev_type, ev_code = parse_event(msg["event"])
        await press(ui, ev_type, ev_code, long=str(msg.get("long", "false")).lower() == "true")
    except Exception as e:
        print(f"error: {e}")
    finally:
        writer.close()


async def main(port):
    ui = UInput(CAPS, name="key-server-kbd")
    print(f"listening on port {port}")
    server = await asyncio.start_server(lambda r, w: handle(r, w, ui), host=None, port=port)
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("-p", "--port", type=int, default=9003)
    asyncio.run(main(**vars(p.parse_args())))
