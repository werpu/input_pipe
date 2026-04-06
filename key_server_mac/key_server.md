# key_server / key_client (macOS)

macOS port of the Linux key_server. Same TCP protocol, same client — only the server differs, using `pynput` instead of `evdev`/`uinput`.

## Building

Run from inside the `key_server_mac/` directory:

```bash
./build.sh
```

Produces two self-contained executables:

```
dist/key_server
dist/key_client
```

## Accessibility permission

macOS requires the app to be granted Accessibility access before it can inject keystrokes. On first run you will get a prompt, or grant it manually:

**System Preferences → Security & Privacy → Privacy → Accessibility**

Add the terminal (or the `key_server` executable itself) to the allowed list.

## key_server

**Start:**

```bash
./dist/key_server              # default port 9003
./dist/key_server -p 9002      # custom port
```

**Protocol** (identical to the Linux version):

```json
{"event": "(EV_KEY), code 28 (KEY_ENTER)"}
{"event": "(EV_KEY), code 28 (KEY_ENTER)", "long": "true"}
```

| Field | Required | Description |
|-------|----------|-------------|
| `event` | yes | evtest-style event string: `(EV_KEY), code <N> (<NAME>)` |
| `long` | no | `"true"` sends 10 repeat presses at 50ms intervals before releasing |
| `to` | no | Accepted but ignored |

The key code number is ignored on macOS — only the name (e.g. `KEY_ENTER`) is used for the lookup.

## key_client

Identical to the Linux client — pure stdlib, no platform dependencies.

**Usage:**

```bash
./dist/key_client <host> <port> "<event>" [long]
```

**Examples:**

```bash
./dist/key_client localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)"
./dist/key_client localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)" long
./dist/key_client localhost 9003 "(EV_KEY), code 103 (KEY_UP)"
./dist/key_client localhost 9003 "(EV_KEY), code 30 (KEY_A)"
```

## Supported keys

| Linux name | macOS action |
|------------|-------------|
| `KEY_ENTER` | Return |
| `KEY_ESC` | Escape |
| `KEY_SPACE` | Space |
| `KEY_BACKSPACE` | Backspace |
| `KEY_TAB` | Tab |
| `KEY_DELETE` | Delete (forward) |
| `KEY_UP/DOWN/LEFT/RIGHT` | Arrow keys |
| `KEY_HOME` / `KEY_END` | Home / End |
| `KEY_PAGEUP` / `KEY_PAGEDOWN` | Page Up / Page Down |
| `KEY_F1` – `KEY_F12` | Function keys |
| `KEY_A` – `KEY_Z` | Letters a–z |
| `KEY_0` – `KEY_9` | Digits 0–9 |
| `KEY_LEFTSHIFT` / `KEY_RIGHTSHIFT` | Shift |
| `KEY_LEFTCTRL` / `KEY_RIGHTCTRL` | Ctrl (Control) |
| `KEY_LEFTALT` / `KEY_RIGHTALT` | Alt (Option) |
| `KEY_LEFTMETA` / `KEY_RIGHTMETA` | Cmd (Command) |
| `KEY_CAPSLOCK` | Caps Lock |
