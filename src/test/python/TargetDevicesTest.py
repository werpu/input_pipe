import unittest

from devices.drivers.keybd import VirtualKeyboard
from devices.drivers.mouse import VirtualMouse
from devices.drivers.xbx360 import Xbox360
from utils.evdevutils import EvDevUtils
from time import sleep


class TargetDevTestCase(unittest.TestCase):

    def test_device_creation(self):
        self.assert_device(Xbox360())
        self.assert_device(VirtualMouse())
        self.assert_device(VirtualKeyboard())

    # Generic dives creation assert routine
    def assert_device(self, device_drv):
        device_drv.create().syn()
        found = False
        cnt = 0
        # give linux time to catch up usually 0.05sec on a semi modern machine
        while cnt < 3 and found is False:
            cnt += 1
            sleep(0.1)
            for dev in EvDevUtils.get_available_devices():
                found = found or dev.phys == device_drv.phys
        self.assertTrue(found, "device created and available")


if __name__ == '__main__':
    unittest.main()
