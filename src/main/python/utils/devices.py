# https://python-evdev.readthedocs.io/en/latest/usage.html
import array as arr
import evdev
import yaml


class Devices:

    def __init__(self):
        self.devices = []
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            self.devices.append(device)



