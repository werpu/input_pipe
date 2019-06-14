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

import yaml
from utils.langutils import *


class Config():

    def __init__(self, configfile='devices.yaml'):
        self.inputs = None
        stream = open(configfile, 'r')
        self.__dict__.update(yaml.load(stream, Loader=yaml.FullLoader))
        stream.close()

    #
    # performs a full match on the supplied parameters
    #
    @staticmethod
    def full_match(device, name, name_re, phys, phys_re, vendor, product):
        matchers = Config.get_match_map(name, name_re, phys, phys_re, product, vendor)

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
    def any_match(device, name, name_re, phys, phys_re, vendor, product):
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
    def get_config_input_params(self, key):
        rel_pos = save_fetch(lambda: self.inputs[key][RELPOS], 1)
        name = save_fetch(lambda: self.inputs[key][NAME])
        phys = save_fetch(lambda: self.inputs[key][PHYS])
        name_re = save_fetch(lambda: self.inputs[key][NAME_RE])
        phys_re = save_fetch(lambda: self.inputs[key][PHYS_RE])
        vendor = save_fetch(lambda: self.inputs[key][INFO][1])
        product = save_fetch(lambda: self.inputs[key][INFO][2])
        exclusive = save_fetch(lambda: self.inputs[key][EXCLUSIVE])

        return name, name_re, phys, phys_re, rel_pos, vendor, product, exclusive


INPUTS = "inputs"
PHYS_RE = "phys_re"
NAME_RE = "name_re"
PHYS = "phys"
NAME = "name"
RELPOS = "relpos"
VENDOR = "vendor"
PRODUCT = "product"
VERSION = "version"
INFO = "info"
EXCLUSIVE = "exclusive"