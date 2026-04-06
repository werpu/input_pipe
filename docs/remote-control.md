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

The `trigger_input` command injects a synthetic event directly into an output device. The argument is a JSON-like dict using evtest-style event strings:

```bash
./input_pipe --server=N --command="trigger_input {'to': 'xbox1', 'event': '(EV_KEY), code 272 (BTN_LEFT)'}"
```

This causes a left-trigger button press on the `xbox1` virtual controller.

**Security note:** There is no authentication on the command server — this is intentional for private local network use cases. Anyone who can reach the port can inject arbitrary input events or stop the process. Keep the port firewalled from untrusted networks.

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
./dist/input_pipe --server=N --command="trigger_input {'to': 'keybd1', 'event': '(EV_KEY), code 28 (KEY_ENTER)'}"

# Press and release the letter 'A' (KEY_A = code 30)
./dist/input_pipe --server=N --command="trigger_input {'to': 'keybd1', 'event': '(EV_KEY), code 30 (KEY_A)'}"

# Press and release the spacebar (KEY_SPACE = code 57)
./dist/input_pipe --server=N --command="trigger_input {'to': 'keybd1', 'event': '(EV_KEY), code 57 (KEY_SPACE)'}"
```

Use `evtest` or refer to the Linux kernel header `linux/input-event-codes.h` to look up key codes for any key you need.

### 4. Scripting a sequence

Because each `trigger_input` call is a separate command, wrap them in a shell script to send a sequence:

```bash
#!/usr/bin/env bash
CMD="./dist/input_pipe --server=N --command"
KBD="keybd1"

send_key() {
  $CMD "trigger_input {'to': '$KBD', 'event': '(EV_KEY), code $1 ($2)'}"
}

send_key 20 KEY_T
send_key 18 KEY_E
send_key 31 KEY_S
send_key 20 KEY_T
send_key 28 KEY_ENTER
```
