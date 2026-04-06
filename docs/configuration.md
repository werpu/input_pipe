# Configuration Reference

A config file has three top-level sections: `inputs`, `outputs`, and `rules`. Examples for all supported formats are in `src/test/resources/`.

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| YAML | `.yaml` | Default; strict indentation |
| JSON5 | `.json5` | Recommended; allows comments and trailing commas |
| TOML | `.toml` | |
| Velocity template | `.vtpl` | Template that renders into one of the above |

For Velocity template syntax see the [Apache Velocity User Guide](https://velocity.apache.org/engine/1.7/user-guide.html). The file `src/test/resources/macros.vm` shows helper macros that reduce boilerplate.

---

## inputs

Defines which physical input devices to capture events from. Each entry has an internal key (used in rules) and a set of match criteria.

```yaml
inputs:

  digital:
    name: Ultimarc I-PAC Ultimarc I-PAC
    exclusive: true
    relpos: 1

  analog_left:
    name_re: ^Ultimarc.*Ultrastik\sPlayer\ 1$
    exclusive: true
    relpos: 1
```

### Match criteria

| Key | Type | Description |
|-----|------|-------------|
| `name` | string | Exact match against the device name reported by the kernel |
| `name_re` | regex | Regular expression match against the device name |
| `phys` | string | Exact match against the device's physical address (`lsinput` shows this) |
| `phys_re` | regex | Regular expression match against the physical address |

Multiple criteria can be combined on one device — all must match. You cannot specify both `name` and `name_re` on the same device.

Use `lsinput` to find device names and physical addresses. Use `evtest` to inspect events.

### Options

| Key | Default | Description |
|-----|---------|-------------|
| `exclusive` | `false` | If `true`, the device is grabbed exclusively so no other program receives its events. Note: `exclusive` locks **all** matched devices, not just the one selected by `relpos`. |
| `relpos` | `1` | When multiple devices match, selects which one to use (ordered by `/dev/input/eventN` node number). |

---

## outputs

Defines the virtual output devices that rules can route events to.

```yaml
outputs:

  xbox1:
    name: Microsoft X-Box 360 pad
    type: xbx360

  keybd1:
    name: key1
    type: keybd

  exec1:
    name: exec1
    type: exec
```

Each entry has an internal key, a `name` exposed to Linux, and a `type`. See [drivers.md](drivers.md) for the full list of types.

---

## rules

Maps input events to output events. Each rule block targets one source device, then lists per-event mappings.

```yaml
rules:
  - from: digital
    target_rules:
      - from_ev: (EV_KEY), code 103 (KEY_UP)
        targets:
          - to: xbox1
            to_ev: (EV_ABS), code 17 (ABS_HAT0Y), value -1
```

### Event string format

`from_ev` and `to_ev` use the same format that `evtest` prints:

```
(EV_TYPE), code NNN (CODE_NAME)
```

The `, value N` suffix on `to_ev` is optional. Include it when you need to emit a different value than the one received (e.g. mapping a key press value of `1` to a d-pad value of `-1`).

For `exec` and `eval` targets, `to_ev` uses `(META), <data>` where `<data>` is a shell command or a path to a Python script respectively.

### Fan-out: one input to multiple outputs

A single `from_ev` can have multiple `targets`:

```yaml
- from_ev: (EV_ABS), code 1 (ABS_Y)
  targets:
    - to: xbox1
      to_ev: (EV_ABS), code 4 (ABS_RY)
    - to: xbox2
      to_ev: (EV_ABS), code 1 (ABS_Y)
```

### Auto-fire / periodical triggers

Add `periodical` and `frequency` to a target to enable auto-repeat:

```yaml
targets:
  - to: xbox1
    to_ev: (EV_KEY), code 103 (KEY_UP), value -1
    periodical: 1   # 1 = fire while held, 2 = toggle on/off
    frequency: 10   # milliseconds between repeats
```

| `periodical` | Behaviour |
|--------------|-----------|
| `0` (default) | Normal, no auto-fire |
| `1` | Auto-fire while the button is held; stops on release |
| `2` | Toggle: first press starts auto-fire, next press stops it |

---

## Full YAML example

```yaml
inputs:
  digital:
    name: Ultimarc I-PAC Ultimarc I-PAC
    exclusive: true
    relpos: 1
  analog_left:
    name_re: ^Ultimarc.*Ultrastik\sPlayer\ 1$
    exclusive: true
    relpos: 1

outputs:
  xbox1:
    name: Microsoft X-Box 360 pad
    type: xbx360
  keybd1:
    name: key1
    type: keybd

rules:
  - from: digital
    target_rules:
      - from_ev: (EV_KEY), code 103 (KEY_UP)
        targets:
          - to: xbox1
            to_ev: (EV_ABS), code 17 (ABS_HAT0Y), value -1

  - from: analog_left
    target_rules:
      - from_ev: (EV_ABS), code 1 (ABS_Y)
        targets:
          - to: xbox1
            to_ev: (EV_ABS), code 4 (ABS_RY)
          - to: xbox1
            to_ev: (EV_KEY), code 103 (KEY_UP)
            periodical: 1
            frequency: 10
```

## Full JSON5 example

JSON5 is recommended because it allows comments and is more forgiving of syntax errors than YAML:

```json5
{
  inputs: {
    digital: {
      name: "Ultimarc I-PAC Ultimarc I-PAC",
      exclusive: true,
      relpos: 1
    }
  },
  outputs: {
    xbox1: {
      name: "Microsoft X-Box 360 pad",
      type: "xbx360"
    }
  },
  rules: [
    {
      from: "digital",
      target_rules: [
        {
          from_ev: "(EV_KEY), code 103 (KEY_UP)",
          targets: [
            {
              to: "xbox1",
              to_ev: "(EV_ABS), code 17 (ABS_HAT0Y), value -1",
              periodical: 1,
              frequency: 10
            }
          ]
        }
      ]
    }
  ]
}
```

## Velocity template example

A `.vtpl` file is rendered by the Velocity engine before being parsed as JSON5 (or YAML/TOML). Define reusable macros in a `macros.vm` file:

```velocity
#parse("macros.vm")

{
  inputs: {
    #input_def( "digital" "Ultimarc I-PAC Ultimarc I-PAC" "true" "1"),
    #input_def( "analog_left" "^Ultimarc.*Ultrastik\\sPlayer\\ 1$" "true" "1")
  },
  outputs: {
    #output_def( "xbox1" "Microsoft X-Box 360 pad" "xbx360")
  },
  rules: [
    {
      from: "digital",
      target_rules: [
        #mapping( "(EV_KEY), code 103 (KEY_UP)" "xbox1" "(EV_ABS), code 17 (ABS_HAT0Y), value -1" )
      ]
    }
  ]
}
```

The built-in macros in `macros.vm` are `#input_def`, `#output_def`, `#output`, and `#mapping`.
