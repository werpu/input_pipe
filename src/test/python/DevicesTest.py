import unittest

from test_utils.devicesMock import DevicesMock
from utils.config import Config


class MyTestCase(unittest.TestCase):

    def test_deviceparsing(self):

        devices = DevicesMock(Config("../resources/devices.yaml"))
        self.assertTrue(len(devices.devices) == 3)


if __name__ == '__main__':
    unittest.main()
