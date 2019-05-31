import unittest
from time import sleep

from ev_core.drivers.keybd import VirtualKeyboard
from ev_core.drivers.mouse import VirtualMouse
from ev_core.drivers.xbx360 import Xbox360
from ev_core.targetdevices import TargetDevices
from ev_core.config import Config
from utils.evdevutils import EvDevUtils


# Tests for the target device capabilities
# We test the driver generation the target device matching
# and the event sendinng here
class TargetDevTestCase(unittest.TestCase):

    def test_device_creation(self):
        self._assert_created_device(Xbox360())
        self._assert_created_device(VirtualMouse())
        self._assert_created_device(VirtualKeyboard())

    # config test for matching devices after creation
    def test_device_match(self):
        devices = TargetDevices(Config("../resources/devices.yaml"))
        self.assertEqual(len(devices.drivers), 4, "3 devices found")
        self.assertTrue(devices.drivers["xbox1"] is not None)
        self.assertTrue(devices.drivers["xbox2"] is not None)
        self.assertTrue(devices.drivers["mouse1"] is not None)
        self.assertTrue(devices.drivers["keybd1"] is not None)

    # Generic dives creation assert routine
    def _assert_created_device(self, device_drv):
        device_drv.create().syn()
        found = False
        cnt = 0
        # give linux time to catch up usually 0.05sec on a semi modern machine
        while cnt < 3 and not found:
            cnt += 1
            sleep(0.1)
            for dev in EvDevUtils.get_available_devices():
                found = found or dev.phys == device_drv.phys
        self.assertTrue(found, "device created and available")


if __name__ == '__main__':
    unittest.main()
