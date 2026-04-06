# key_server / key_client

A minimal standalone TCP keyboard injection server and its matching client. No configuration files, no dependencies beyond `evdev`.

## Building

Run from inside the `key_server/` directory:

```bash
./build.sh
```

Produces two self-contained executables:

```
dist/key_server
dist/key_client
```

The server requires `evdev` (Linux only). The client is pure stdlib and runs anywhere.

## key_server

Creates a single virtual keyboard device via uinput and listens for JSON keystroke commands over TCP. One command per connection.

**Start:**

```bash
./dist/key_server              # default port 9003
./dist/key_server -p 9002      # custom port
```

**Protocol:**

Each connection sends one or more newline-terminated JSON objects, then closes:

```json
{"event": "(EV_KEY), code 28 (KEY_ENTER)"}
{"event": "(EV_KEY), code 28 (KEY_ENTER)", "long": "true"}
```

| Field | Required | Description |
|-------|----------|-------------|
| `event` | yes | evtest-style event string: `(EV_KEY), code <N> (<NAME>)` |
| `long` | no | `"true"` sends 10 repeat events (value `2`) at 50ms intervals before releasing, simulating a held key |
| `to` | no | Accepted but ignored — there is only one virtual keyboard device |

Use `evtest` to find key codes, or refer to `linux/input-event-codes.h`.

**Permissions:**

The server needs write access to `/dev/uinput`. Either run as root or grant access via udev:

```
SUBSYSTEM=="misc", KERNEL=="uinput", MODE="0660", GROUP="input"
```

Then add your user to the `input` group.

## key_client

Sends a single keystroke command to a running `key_server`.

**Usage:**

```bash
./dist/key_client <host> <port> "<event>[;<event>...]"
```

Separate multiple keystrokes with `;`. Append `:long` for a long press.

**Examples:**

```bash
# Enter key
./dist/key_client localhost 9003 "(EV_KEY), code 28 (KEY_ENTER)"

# Held Enter key (long press)
./dist/key_client localhost 9003 "(EV_KEY), code 28 (KEY_ENTER):long"

# Arrow up
./dist/key_client localhost 9003 "(EV_KEY), code 103 (KEY_UP)"

# Type "hello" + Enter in one connection
./dist/key_client localhost 9003 "(EV_KEY), code 35 (KEY_H);(EV_KEY), code 18 (KEY_E);(EV_KEY), code 38 (KEY_L);(EV_KEY), code 38 (KEY_L);(EV_KEY), code 24 (KEY_O);(EV_KEY), code 28 (KEY_ENTER)"
```

Alternatively, `netcat` works for single keystrokes:

```bash
printf '{"event": "(EV_KEY), code 28 (KEY_ENTER)"}\n' | nc <host> 9003
```

## Common key codes

| Key | Code |
|-----|------|
| `KEY_ENTER` | 28 |
| `KEY_ESC` | 1 |
| `KEY_SPACE` | 57 |
| `KEY_BACKSPACE` | 14 |
| `KEY_UP` | 103 |
| `KEY_DOWN` | 108 |
| `KEY_LEFT` | 105 |
| `KEY_RIGHT` | 106 |
| `KEY_A` – `KEY_Z` | 30 – 44 (non-sequential, use evtest to confirm) |
| `KEY_F1` – `KEY_F12` | 59 – 88 |
| `KEY_LEFTCTRL` | 29 |
| `KEY_LEFTSHIFT` | 42 |
| `KEY_LEFTALT` | 56 |
