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


from ev_core.config import Config, NAME
from utils.langutils import *
from ev_core.drivers.driverregistry import DEV_TYPES


class TargetDevices:

    def __init__(self, config: Config):

        self.config = config
        self.drivers = {}

        for key in config.outputs:
            dev_key, dev_name, dev_type = self.get_config_data(key)

            driver = save_fetch(lambda: DEV_TYPES[dev_type](), None)

            if driver is not None:
                driver.create()
                self.drivers[dev_key] = driver
                print("Output driver found for "+dev_key + " node created with phys " + save_fetch(lambda: driver.phys))

    # Fetches the associated config data
    def get_config_data(self, key):
        dev_key = key
        dev_name = save_fetch(lambda: self.config.outputs[key][NAME], None)
        dev_type = save_fetch(lambda: self.config.outputs[key]["type"], None)

        return dev_key, dev_name, dev_type

