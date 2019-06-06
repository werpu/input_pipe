import unittest

from ev_core.config import Config
from test_utils.eventControllerMock import EventControllerMock
from test_utils.udevDeviceMock import UdevDeviceMock
from test_utils.udevListenerMock import UdevListenerMock


class MyTestCase(unittest.TestCase):
    def test_udev_event_handling(self):
        config = Config("../resources/devices.yaml")
        eventcontroller = EventControllerMock(config)
        listener = UdevListenerMock(eventcontroller)

        device1 = UdevDeviceMock("Ultimarc_UltraStik", "Ultimarc_Ultra-Stik_Player_1")
        self.assertTrue(eventcontroller.started)
        self.assertTrue(eventcontroller.restarted_cnt == 0)
        listener.trigger_event_usb("remove", device1)
        self.assertFalse(eventcontroller.started)
        listener.trigger_event_input("add", device1)
        self.assertTrue(eventcontroller.started)
        self.assertTrue(eventcontroller.restarted_cnt > 0)


if __name__ == '__main__':
    unittest.main()
