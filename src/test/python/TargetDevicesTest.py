import unittest

from devices.drivers.keybd import VirtualKeyboard
from devices.drivers.mouse import VirtualMouse
from devices.drivers.xbx360 import Xbox360
from devices.targetdevices import TargetDevices
from utils.config import Config
from utils.evdevutils import EvDevUtils
from time import sleep


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
        print("todo implement me")

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
