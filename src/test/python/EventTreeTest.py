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
