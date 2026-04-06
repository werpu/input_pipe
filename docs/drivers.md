# Output Drivers

Output drivers back the virtual devices defined in the `outputs` section of a config file. Each driver type emits a different kind of event to the Linux kernel or to an external process.

## Built-in driver types

### `xbx360` — Xbox 360 controller

Creates a virtual Xbox 360 gamepad via uinput. Use standard `EV_ABS` / `EV_KEY` event codes.

```yaml
outputs:
  xbox1:
    name: Microsoft X-Box 360 pad
    type: xbx360
```

### `keybd` — Virtual keyboard

Creates a virtual keyboard via uinput.

```yaml
outputs:
  keybd1:
    name: key1
    type: keybd
```

### `mouse` — Virtual mouse

Creates a virtual mouse via uinput. Map to `EV_REL` / `EV_KEY` mouse event codes.

```yaml
outputs:
  mouse1:
    name: mouse
    type: mouse
```

### `serial` — Serial device

Writes events to a serial port.

```yaml
outputs:
  serial1:
    name: serial1
    type: serial
```

### `exec` — Execute a shell command

Runs an arbitrary shell command when an input event fires. The command is provided in the rule's `to_ev` field using `(META), <command>`. The command is only executed on value `1` (button press).

```yaml
outputs:
  exec1:
    name: exec1
    type: exec
```

Rule example:

```yaml
- to: exec1
  to_ev: (META), /usr/local/bin/4way
```

### `eval` — Execute a Python script

Runs a Python script file when an input event fires (on value `>= 1`). The script path is given in `to_ev` as `(META), <path>`. The script receives the following variables in its execution context:

| Variable | Description |
|----------|-------------|
| `config` | The current `Config` object |
| `drivers` | Dict of all instantiated driver objects |
| `meta` | The path string from `to_ev` |
| `event` | The raw evdev event that triggered the rule |

Scripts are compiled and cached on first use.

```yaml
outputs:
  eval1:
    name: eval1
    type: eval
```

Rule example:

```yaml
- to: eval1
  to_ev: (META), /home/user/scripts/my_macro.py
```

---

## Writing a custom driver

Drivers live in `src/main/python/ev_core/drivers/`. Each driver is a class that extends `BaseDriver` (or implements the same interface for non-uinput drivers like `exec`/`eval`).

**Minimal driver skeleton:**

```python
from ev_core.drivers.basedriver import BaseDriver
from ev_core.config import Config


class MyDriver(BaseDriver):

    def __init__(self):
        # initialise any state; no uinput device created yet
        pass

    def create(self, meta=None):
        # called once at startup; create the uinput device here if needed
        # for uinput-backed drivers, call super().create() after setting
        # self.capabilities, self.name, self.vendor, etc.
        pass

    def write(self, config: Config, drivers, e_type, e_sub_type, value,
              meta=None, periodical=0, frequency=0, event=None):
        # called for every matched input event
        pass

    def close(self):
        # clean up; called on shutdown or reload
        pass

    def syn(self):
        # send a sync event if backed by uinput; otherwise pass
        pass
```

**Register the driver** by adding it to the `DEV_TYPES` dict in `src/main/python/ev_core/drivers/driverregistry.py`:

```python
from ev_core.drivers.mydriver import MyDriver

DEV_TYPES = {
    # ... existing entries ...
    "mytype": MyDriver,
}
```

The key (`"mytype"`) becomes the value you use for `type:` in the `outputs` section of a config file.

### Auto-fire support

`BaseDriver.write()` handles the `periodical` and `frequency` rule fields automatically for uinput-backed drivers. Non-uinput drivers (like `exec`/`eval`) implement `write()` directly and ignore those fields.
