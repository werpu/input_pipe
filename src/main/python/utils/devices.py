# https://python-evdev.readthedocs.io/en/latest/usage.html
import evdev
from utils.config import Config, PHYS_RE, NAME_RE, PHYS, NAME, RELPOS
from utils.langutils import *


# A device holder class
# determines the devices in the input devices
# section and then stores the ones which match from
# the inputs section of the config
class Devices:

    def __init__(self, config: Config):
        self.devices = []
        self.matched = {}
        self.config = config

        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]

        for device in devices:
            if self._device_match(device):
                self.devices.append(device)

    # Complex device match, it basically first
    # checks for a full name or phys match
    # and if not found tries a re match for name or phys
    # also takes the rel device position into consideration
    # which is the relativ device in multiple matches
    def _device_match(self, device: evdev.InputDevice):
        for key in tree_fetch(lambda: self.config.inputs, {}):
            name, name_re, phys, phys_re, rel_pos = self._get_config_input_params(key)
            found = self._match(device, name, name_re, phys, phys_re)

            if found:
                accessor_key = name or phys or name_re or phys_re
                already_processed = tree_fetch(lambda: self.matched[accessor_key], 1)
                if already_processed == rel_pos:
                    return True
                else:
                    self.matched[accessor_key] = already_processed + 1
        return False

    @staticmethod
    def _match(device, name, name_re, phys, phys_re):
        found = False

        if caseless_equal(device.name or "", name or DUMMY_DEFAULT):
            found = True
        elif re_match(device.phys or "", phys or DUMMY_DEFAULT):
            found = True
        elif caseless_equal(device.name or "", name_re or DUMMY_DEFAULT):
            found = True
        elif re_match(device.phys or "", phys_re or DUMMY_DEFAULT):
            found = True
        return found

    # fetches all the input params from the vonfig at position inputs.<key>
    def _get_config_input_params(self, key):
        rel_pos = tree_fetch(lambda: self.config.inputs[key][RELPOS], 1)
        name = tree_fetch(lambda: self.config.inputs[key][NAME])
        phys = tree_fetch(lambda: self.config.inputs[key][PHYS])
        name_re = tree_fetch(lambda: self.config.inputs[key][NAME_RE])
        phys_re = tree_fetch(lambda: self.config.inputs[key][PHYS_RE])

        return name, name_re, phys, phys_re, rel_pos




