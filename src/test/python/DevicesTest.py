import unittest

from test_utils.devicesMock import DevicesMock
from utils.config import Config


class MyTestCase(unittest.TestCase):

    def test_device_parsing(self):

        devices = DevicesMock(Config("../resources/devices.yaml"))
        self.assertTrue(len(devices.devices) == 3)
        self.assertEqual(devices.devices[2].name, 'Ultimarc UltraStik Ultimarc UltraStik Player 2')
        self.assertEqual(devices.devices[1].name, 'Ultimarc UltraStik Ultimarc UltraStik Player 1')
        self.assertEqual(devices.devices[0].name, 'Ultimarc I-PAC Ultimarc I-PAC')


if __name__ == '__main__':
    unittest.main()
