# https://python-evdev.readthedocs.io/en/latest/usage.html
import evdev
from utils.config import Config, INPUTS, PHYS_RE, NAME_RE, PHYS, NAME, RELPOS
from utils.langutils import *


class Devices:

    def __init__(self, config: Config):
        self.devices = []
        self.matched = {}
        self.config = config
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        for device in devices:
            if self.device_match(device):
                self.devices.append(device)

    # Complex device match, it basically first
    # checks for a full name or phys match
    # and if not found tries a re match for name or phys
    # also takes the rel device position into consideration
    # which is the relativ device in multiple matches
    def device_match(self, device: evdev.InputDevice):
        for key in el_vis(lambda: self.config[INPUTS], {}):
            found = False
            rel_pos = el_vis(lambda: self.config[key][RELPOS], 1)
            name = el_vis(lambda: self.config[key][NAME], None)
            phys = el_vis(lambda: self.config[key][PHYS], None)
            name_re = el_vis(lambda: self.config[key][NAME_RE], None)
            phys_re = el_vis(lambda: self.config[key][PHYS_RE], None)

            if caseless_equal(device.name, name or DUMMY_DEFAULT):
                found = True
            elif re_match(device.phys or "", phys or DUMMY_DEFAULT):
                found = True
            elif caseless_equal(device.name, name_re or DUMMY_DEFAULT):
                found = True
            elif re_match(device.phys or "", phys_re or DUMMY_DEFAULT):
                found = True

            if found:
                accessor_key = name or phys or name_re or phys_re
                already_processed = el_vis(lambda: self.matched[accessor_key], 1)
                if already_processed == rel_pos:
                    return True
                else:
                    self.matched[accessor_key] = already_processed + 1

        return False


