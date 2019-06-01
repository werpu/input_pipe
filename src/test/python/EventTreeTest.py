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

import unittest

from test_utils.sourceDevicesMock import SourceDevicesMock
from ev_core.targetdevices import TargetDevices
from ev_core.eventtree import EventTree
from ev_core.config import Config
from utils.langutils import *


class MyTestCase(unittest.TestCase):

    def test_tree_buildup(self):
        config = Config("../resources/devices.yaml")
        source_devices = SourceDevicesMock(config)
        target_devices = TargetDevices(config)
        event_tree = EventTree(config, source_devices, target_devices)
        self.assertIsNotNone(save_fetch(lambda: event_tree.tree["digital"]["EV_KEY"]["103"]["xbox1"]["driver"]))
        self.assertIsNotNone(save_fetch(lambda: event_tree.tree["analog_left"]["EV_KEY"]["103"]["xbox1"]["driver"]))
        self.assertIsNotNone(save_fetch(lambda: event_tree.tree["analog_left"]["EV_KEY"]["103"]["xbox2"]["driver"]))



if __name__ == '__main__':
    unittest.main()
