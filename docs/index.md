# Input Pipe

Input Pipe is a universal Linux input device mapper and event multiplexer. It reads events from multiple physical input devices (joysticks, arcade panels, keyboards, etc.) and routes them to multiple virtual output devices via a single configuration file.

## Why Input Pipe?

Existing tools like Moltengamepad, XboxDrv, and Joy2Key tend to support only one joystick at a time or constrain the mapping in some way. Input Pipe was built for complex m:n (many-to-many) use cases — for example, a custom arcade panel with dozens of buttons, two analog sticks, two spinners, two digital sticks, and a trackball.

**Key properties:**

- Maps any input event to any output event, across any number of devices
- Supports hotplugging — no udev rules needed
- Dynamic reconfiguration via remote commands and overlays at runtime
- Configurable in YAML, JSON5, TOML, or Velocity templates

## Quick Start

```bash
# Install dependencies
./setup.sh

# Run with your config file
pipenv run python ./src/main/python/input_pipe.py -c devices.yaml

# Or use a pre-built executable
./dist/input_pipe -c devices.yaml
```

See [installation.md](installation.md) for setup details and [configuration.md](configuration.md) for a full reference on writing config files.

## Docs

| File | Contents |
|------|----------|
| [installation.md](installation.md) | Setup, dependencies, running as a system service |
| [configuration.md](configuration.md) | Full config reference: inputs, outputs, rules, formats |
| [drivers.md](drivers.md) | Output driver types and how to write a custom driver |
| [remote-control.md](remote-control.md) | Server mode, remote commands, overlays |
