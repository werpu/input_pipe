# Installation

## Prerequisites

- Linux (the program depends on the evdev/uinput kernel interfaces)
- Python 3.7.3
- [pipenv](https://pipenv.pypa.io/)
- pyinstaller (only needed to build the executable)

## Setup

```bash
./setup.sh
```

This installs all Python dependencies via pipenv, including evdev, pyudev, uvloop, pyyaml, json5, toml, and others declared in `Pipfile`.

## Running

**From source:**

```bash
pipenv run python ./src/main/python/input_pipe.py -c <config_file>
```

**Pre-built executable** (x64 Linux, provided in `dist/`):

```bash
./dist/input_pipe -c <config_file>
```

**Build your own executable:**

```bash
./build.sh
```

This runs PyInstaller and places the result at `./dist/input_pipe`.

See [Building a self-contained executable](#building-a-self-contained-executable) below for full details including ARM.

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `-c` / `--config` | `./devices.yaml` | Path to the config file |
| `-p` / `--port` | `-1` (disabled) | TCP port for the remote command server |
| `-pd` / `--pidfile` | `/tmp/input_pipe.pid` | PID file location |
| `-s` / `--server` | `Y` | Run as server (`Y`) or send a command (`N`) |
| `-cm` / `--command` | — | Remote command to send to a running server |

## Building a self-contained executable

PyInstaller bundles the Python interpreter and all dependencies into a single binary that can be copied to any compatible Linux machine without installing Python or pipenv.

**Important:** PyInstaller cannot cross-compile. The binary must be built on the same CPU architecture as the target machine. Build on x64 for x64, build on ARM for ARM.

### Steps

```bash
# 1. Install dependencies (only needed once)
./setup.sh

# 2. Build the executable
./build.sh
```

The result is `./dist/input_pipe` — a standalone binary with no external dependencies.

### ARM (Raspberry Pi)

Run the same two commands on the ARM device itself. The resulting binary is native to that architecture (armv7l and aarch64 binaries are not interchangeable).

If your OS ships a newer Python than 3.7.3, install 3.7.3 via `pyenv` first and make sure `pipenv` picks it up:

```bash
pyenv install 3.7.3
pyenv local 3.7.3
./setup.sh
./build.sh
```

Alternatively, relax the Python version pin in `Pipfile` from `python_version = "3.7"` to `python_version = "3"` — the codebase has no hard dependency on 3.7 specifically.

### What `build.sh` does

```bash
pipenv run pyinstaller -s -n input_pipe --onefile --distpath ./dist/ \
    ./src/main/python/input_pipe.py
```

- `--onefile` — packages everything into a single executable
- `-s` — strips debug symbols to reduce binary size
- `-n input_pipe` — sets the output file name
- `--distpath ./dist/` — output directory

## Running as a System Service

Input Pipe handles its own hotplug detection, so no udev rules are required. You can plug it into systemd or init.d directly.

Example systemd unit (`/etc/systemd/system/input_pipe.service`):

```ini
[Unit]
Description=Input Pipe device mapper
After=multi-user.target

[Service]
Type=simple
User=<your_user>
ExecStart=/path/to/dist/input_pipe -c /path/to/devices.yaml
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Run as a regular user rather than root where possible — the program only needs read access to `/dev/input/` devices and write access to `/dev/uinput`.

## Permissions

To access `/dev/uinput` without root, add your user to the `input` group or create a udev rule:

```
SUBSYSTEM=="misc", KERNEL=="uinput", MODE="0660", GROUP="input"
```

To read from input devices (`/dev/input/eventN`) without root:

```
SUBSYSTEM=="input", MODE="0660", GROUP="input"
```
