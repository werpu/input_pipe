# Remote Control

Input Pipe can expose a TCP command server that lets you control a running instance from the command line without restarting it.

## Enabling the server

Start Input Pipe with a `-p` port number:

```bash
./input_pipe -p 9002 -c devices.yaml
```

The server listens on the given port. By default the port is `-1` (disabled).

## Sending commands

Send a command to a running server by starting a second invocation with `--server=N`:

```bash
./input_pipe --server=N --command=<command>
```

The sender discovers the running server's port automatically via the Announcer service.

## Supported commands

| Command | Description |
|---------|-------------|
| `stop` | Stops the running server process |
| `reload` | Reloads the config file and restarts the event pipeline without killing the process |
| `overlay <filename>` | Pushes a config overlay onto the overlay stack |
| `pop_overlay` | Removes the most recently added overlay |
| `remove_overlay <filename>` | Removes a specific overlay by filename regardless of stack position |
| `reset_overlay` | Removes all overlays and restores the original configuration |
| `trigger_input <json>` | Sends a synthetic input event directly to an output device |

Unknown commands are silently ignored.

---

## Overlays

An overlay is a partial config file that is merged on top of the running configuration. It can add new rules or override existing ones without replacing the entire config.

- Overlays are processed last-in-first-out: the most recently added overlay takes precedence.
- Only the `rules` section is typically present in an overlay; `inputs` and `outputs` are optional.
- The original config is fully restored when all overlays are removed.

**Overlay file example** (`src/test/resources/overlay.yaml`):

```yaml
rules:
  - from: analog_left
    target_rules:
      - from_ev: (EV_KEY), code 105 (KEY_UP)
        targets:
          - to: booga1
            to_ev: (META), overlayed
```

**Managing overlays:**

```bash
# Add an overlay
./input_pipe --server=N --command="overlay /path/to/overlay.yaml"

# Remove the top overlay
./input_pipe --server=N --command=pop_overlay

# Remove a specific overlay
./input_pipe --server=N --command="remove_overlay /path/to/overlay.yaml"

# Remove all overlays
./input_pipe --server=N --command=reset_overlay
```

### Use case

Overlays are useful when certain games need a different button layout or autofire settings. You can push an overlay when launching a game and pop it when quitting, without ever restarting Input Pipe.

---

## Triggering inputs programmatically

The `trigger_input` command injects a synthetic event directly into an output device. The argument is a JSON object using evtest-style event strings:

```bash
./input_pipe --server=N --command="trigger_input {'to': 'xbox1', 'event': '(EV_KEY), code 272 (BTN_LEFT)'}"
```

This causes a left-trigger button press on the `xbox1` virtual controller.

**Security note:** There is no authentication on the command server — this is intentional for private local network use cases. Anyone who can reach the port can inject arbitrary input events or stop the process. Keep the port firewalled from untrusted networks.

---

## trigger_input wire protocol

This section documents the full protocol used when sending events over a raw TCP connection — as used by the **Multipad** touchpad client.

### Wire format

```
trigger_input <json>\n
```

The message is a single line: the literal string `trigger_input`, a space, then a JSON object. No framing or length prefix — newline-terminated.

### JSON fields

| Field   | Type   | Required | Description |
|---------|--------|----------|-------------|
| `to`    | string | yes      | Target output device name as defined in the config (e.g. `"keybd1"`) |
| `event` | string | yes      | evtest-style event string — see format below |
| `long`  | string | no       | `"true"` to simulate a held key (see below) |

### Event string format

```
(EV_KEY), code <linux_code> (<name>), value <v>
```

- `<linux_code>` — numeric Linux input event code (e.g. `28`)
- `<name>` — symbolic key name (e.g. `KEY_ENTER`)
- `value` suffix — controls key state:
  - `value 1` — key down
  - `value 0` — key up
  - `value 2` — key repeat (auto-generated on long press, see below)

When no `value` suffix is present the server interprets the event as a single press without explicit up/down state.

### Long-press simulation (`"long": "true"`)

When `long` is `"true"`, after the initial key-down event the server automatically sends **10 repeat events** (`value 2`) with **50 ms delays** between each, simulating a physically held key. The client is responsible for sending a separate key-up event afterwards.

### Examples

```bash
# Key down — press Enter
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 28 (KEY_ENTER), value 1", "long": "false"}' | nc <host> 9002

# Key up — release Enter
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 28 (KEY_ENTER), value 0", "long": "false"}' | nc <host> 9002

# Long-press Enter (sends value 1 + 10x value 2 at 50 ms intervals)
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 28 (KEY_ENTER), value 1", "long": "true"}' | nc <host> 9002

# SHIFT + A (two separate key-down messages followed by two key-up messages)
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 42 (KEY_LEFTSHIFT), value 1", "long": "false"}' | nc <host> 9002
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 30 (KEY_A), value 1", "long": "false"}' | nc <host> 9002
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 30 (KEY_A), value 0", "long": "false"}' | nc <host> 9002
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 42 (KEY_LEFTSHIFT), value 0", "long": "false"}' | nc <host> 9002
```

Use `evtest` or the Linux kernel header `linux/input-event-codes.h` to look up key codes.

---

## Example: injecting keystrokes from the network

This is useful when you want a remote process (another machine on the local network, a script, an emulator frontend) to send keyboard input into a running Input Pipe instance.

### 1. Config file (`keyboard_server.yaml`)

Only an `outputs` section is needed — no physical input devices required if all input comes via `trigger_input`:

```yaml
outputs:
  keybd1:
    name: virtual-keyboard
    type: keybd

# inputs can be omitted or left empty if no physical devices are needed
inputs: {}
rules: []
```

### 2. Start Input Pipe with the command server enabled

```bash
./dist/input_pipe -p 9002 -c keyboard_server.yaml
```

### 3. Inject keystrokes from any machine on the network

From the same machine or any other host that can reach port 9002:

```bash
# Press and release the Enter key
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 28 (KEY_ENTER), value 1", "long": "false"}' | nc <host> 9002
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 28 (KEY_ENTER), value 0", "long": "false"}' | nc <host> 9002

# Press and release the letter 'A' (KEY_A = code 30)
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 30 (KEY_A), value 1", "long": "false"}' | nc <host> 9002
echo -n 'trigger_input {"to": "keybd1", "event": "(EV_KEY), code 30 (KEY_A), value 0", "long": "false"}' | nc <host> 9002
```

### 4. Scripting a sequence

```bash
#!/usr/bin/env bash
HOST=<host>
PORT=9002
KBD="keybd1"

send_key() {
  local code=$1 name=$2
  echo -n "trigger_input {\"to\": \"$KBD\", \"event\": \"(EV_KEY), code $code ($name), value 1\", \"long\": \"false\"}" | nc "$HOST" "$PORT"
  echo -n "trigger_input {\"to\": \"$KBD\", \"event\": \"(EV_KEY), code $code ($name), value 0\", \"long\": \"false\"}" | nc "$HOST" "$PORT"
}

send_key 20 KEY_T
send_key 18 KEY_E
send_key 31 KEY_S
send_key 20 KEY_T
send_key 28 KEY_ENTER
```
