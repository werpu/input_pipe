# https://python-evdev.readthedocs.io/en/latest/usage.html
import evdev
from utils.config import Config, PHYS_RE, NAME_RE, PHYS, NAME, RELPOS, VENDOR, PRODUCT, INFO
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

        devices = self.get_available_devices()

        for device in devices:
            if self._device_match(device):
                self.devices.append(device)

    # externalized producer to be replaced in testing cases by mocks
    @staticmethod
    def get_available_devices():
        return [evdev.InputDevice(path) for path in evdev.list_devices()]

    # Complex device match, it basically first
    # checks for a full name or phys match
    # and if not found tries a re match for name or phys
    # also takes the rel device position into consideration
    # which is the relativ device in multiple matches
    def _device_match(self, device: evdev.InputDevice):
        for key in tree_fetch(lambda: self.config.inputs, {}):
            name, name_re, phys, phys_re, rel_pos, vendor, product = self._get_config_input_params(key)
            found = self._full_match(device, name, name_re, phys, phys_re, vendor, product)

            if found:
                accessor_key = name or phys or name_re or phys_re or vendor or product
                already_processed = tree_fetch(lambda: self.matched[accessor_key], 1)
                if already_processed == rel_pos:
                    return True
                else:
                    self.matched[accessor_key] = already_processed + 1
        return False

    #
    # performs a full match on the supplied parameters
    #
    @staticmethod
    def _full_match(device, name, name_re, phys, phys_re, vendor, product):
        matchers = {}
        # we also could iterate over the arguments but for the sake
        # of the name mangling we do not
        if name is not None:
            matchers[NAME] = name
        if name_re is not None:
            matchers[NAME_RE] = name_re
        if phys is not None:
            matchers[PHYS] = phys
        if phys_re is not None:
            matchers[PHYS_RE] = phys_re
        if vendor is not None:
            matchers[VENDOR] = vendor
        if vendor is not None:
            matchers[PRODUCT] = product

        found = True
        for key in matchers:
            dev_key = key
            # vendor and product need special handling coming from the lib
            if dev_key == VENDOR:
                found = found and caseless_equal(device.__getattribute__(INFO)[1], matchers[key])
            elif dev_key == product:
                found = found and caseless_equal(device.__getattribute__(INFO)[2], matchers[key])
            elif re_match(key, "^.*_re$"):
                dev_key = dev_key[:-3]
                found = found and re_match(device.__getattribute__(dev_key), matchers[key])
            else:
                found = found and caseless_equal(device.__getattribute__(key), matchers[key])

        return found


    #
    # triggers if any of the supplied criteria matches
    #
    @staticmethod
    def _any_match(device, name, name_re, phys, phys_re, vendor, product):
        found = False

        if caseless_equal(device.name or "", name or DUMMY_DEFAULT):
            found = True
        elif re_match(device.phys or "", phys or DUMMY_DEFAULT):
            found = True
        elif re_match(device.vendor or "", vendor or DUMMY_DEFAULT):
            found = True
        elif re_match(device.product or "", product or DUMMY_DEFAULT):
            found = True
        elif re_match(device.name or "", name_re or DUMMY_DEFAULT):
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
        vendor = tree_fetch(lambda: self.config.inputs[key][INFO][1])
        product = tree_fetch(lambda: self.config.inputs[key][INFO][2])

        return name, name_re, phys, phys_re, rel_pos, vendor, product




