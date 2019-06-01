# MIT License
#
# Copyright (c) 2019 Werner Punz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# https://python-evdev.readthedocs.io/en/latest/usage.html
import evdev
from ev_core.config import Config, PHYS_RE, NAME_RE, PHYS, NAME, RELPOS, VENDOR, PRODUCT, INFO
from utils.evdevutils import EvDevUtils
from utils.langutils import *


# A device holder class
# determines the devices in the input devices
# section and then stores the ones which match from
# the inputs section of the config
class SourceDevices:

    def __init__(self, config: Config):
        self.devices = []
        self.matched = {}
        self.config = config

        self._matched_devices = {}

        #event tree which is built up from outside
        #which maps the incoming pattern to the output devices
        #in the fastest possible manner
        self._event_tree = {}

        devices = self.get_available_devices()

        for device in devices:
            if self._device_match(device):
                self.devices.append(device)
        if len(self.devices) > 0:
            print("Following devices were found:")
            for device in self.devices:
                print("  - "+device.name)

    # externalized producer to be replaced in testing cases by mocks
    @staticmethod
    def get_available_devices():
        return EvDevUtils.get_available_devices()

    # Complex device match, it basically first
    # checks for a full name or phys match
    # and if not found tries a re match for name or phys
    # also takes the rel device position into consideration
    # which is the relativ device in multiple matches
    def _device_match(self, device: evdev.InputDevice):

        for key in save_fetch(lambda: self.config.inputs, {}):
            name, name_re, phys, phys_re, rel_pos, vendor, product = self._get_config_input_params(key)

            device_match_string = str(self.config.inputs[key])

            found = self._full_match(device, name, name_re, phys, phys_re, vendor, product)

            if found:
                if save_fetch(lambda: self._matched_devices[device_match_string], False) is True:
                    return False
                accessor_key = name or phys or name_re or phys_re or vendor or product
                already_processed = save_fetch(lambda: self.matched[accessor_key], 1)
                if already_processed == rel_pos:
                    self._matched_devices[device_match_string] = True
                    return True
                else:
                    self.matched[accessor_key] = already_processed + 1
        return False

    #
    # performs a full match on the supplied parameters
    #
    @staticmethod
    def _full_match(device, name, name_re, phys, phys_re, vendor, product):
        matchers = SourceDevices.get_match_map(name, name_re, phys, phys_re, product, vendor)

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

    @staticmethod
    def get_match_map(name, name_re, phys, phys_re, product, vendor):
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
        return matchers

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
        rel_pos = save_fetch(lambda: self.config.inputs[key][RELPOS], 1)
        name = save_fetch(lambda: self.config.inputs[key][NAME])
        phys = save_fetch(lambda: self.config.inputs[key][PHYS])
        name_re = save_fetch(lambda: self.config.inputs[key][NAME_RE])
        phys_re = save_fetch(lambda: self.config.inputs[key][PHYS_RE])
        vendor = save_fetch(lambda: self.config.inputs[key][INFO][1])
        product = save_fetch(lambda: self.config.inputs[key][INFO][2])

        return name, name_re, phys, phys_re, rel_pos, vendor, product




