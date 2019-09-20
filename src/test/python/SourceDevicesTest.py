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

import asyncio

from test_utils.sourceDevicesMock import SourceDevicesMock
from ev_core.config import Config


class MyTestCase(unittest.TestCase):

    def test_device_parsing(self):

        self.devices = SourceDevicesMock(Config("../resources/devices.yaml"))

        asyncio.run(self.assertAll())

    async def assertAll(self):

        while not self.devices.all_found:
            await asyncio.sleep(5)

        self.assertTrue(len(self.devices.devices) == 3)
        self.assertEqual(self.devices.devices[2].name, 'Ultimarc UltraStik Ultimarc UltraStik Player 2')
        self.assertEqual(self.devices.devices[1].name, 'Ultimarc UltraStik Ultimarc UltraStik Player 1')
        self.assertEqual(self.devices.devices[0].name, 'Ultimarc I-PAC Ultimarc I-PAC')


if __name__ == '__main__':
    unittest.main()
