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

from ev_core.sourcedevices2 import SourceDevices2
from ev_core.config import Config
from test_utils.deviceMock import DeviceMock


class SourceDevicesMock(SourceDevices2):

    def __init__(self, config: Config):
        SourceDevices2.__init__(self, config)

    def get_available_devices(self):
        return [
            DeviceMock("/dev/input/event3", ["BUS_USB", "0xd209", "0x410", "273"], "Ultimarc I-PAC Ultimarc I-PAC", "usb-0000:38:00.3-3.2/input0", "8"),
            DeviceMock("/dev/input/event4", ["BUS_USB", "0xd209", "0x410", "273"], "Ultimarc I-PAC Ultimarc I-PAC", "usb-0000:38:00.3-3.2/input1", "8"),
            DeviceMock("/dev/input/event5", ["BUS_USB", "0xd209", "0x410", "273"], "Ultimarc I-PAC Ultimarc I-PAC System Control", "usb-0000:38:00.3-3.2/input2", "8"),
            DeviceMock("/dev/input/event6", ["BUS_USB", "0xd209", "0x410", "273"], "Ultimarc I-PAC Ultimarc I-PAC Consumer Control", "usb-0000:38:00.3-3.2/input2", "8"),
            DeviceMock("/dev/input/event7", ["BUS_USB", "0xd209", "0x410", "273"], "Ultimarc I-PAC Ultimarc I-PAC", "usb-0000:38:00.3-3.2/input2", "8"),
            DeviceMock("/dev/input/event8", ["BUS_USB", "0xd209", "0x410", "273"], "Ultimarc I-PAC Ultimarc I-PAC", "usb-0000:38:00.3-3.2/input2", "8"),
            DeviceMock("/dev/input/event9", ["BUS_USB", "0xd209", "0x410", "273"], "Universal Human Interface Device", "usb-0000:38:00.3-3.1.2/input0", "9"),
            DeviceMock("/dev/input/event10", ["BUS_USB", "0xd209", "0x511", "273"], "Ultimarc UltraStik Ultimarc UltraStik Player 1", "usb-0000:38:00.3-3.3/input0", "1"),
            DeviceMock("/dev/input/event11", ["BUS_USB", "0xd209", "0x511", "273"], "Ultimarc UltraStik Ultimarc UltraStik Player 1", "usb-0000:38:00.3-3.3/input1", "1"),
            DeviceMock("/dev/input/event12", ["BUS_USB", "0xd209", "0x511", "273"], "Ultimarc UltraStik Ultimarc UltraStik Player 1", "usb-0000:38:00.3-3.3/input2", "1"),
            DeviceMock("/dev/input/event13", ["BUS_USB", "0xd209", "0x512", "273"], "Ultimarc UltraStik Ultimarc UltraStik Player 2", "usb-0000:38:00.3-3.1.3/input0", "1"),
            DeviceMock("/dev/input/event14", ["BUS_USB", "0xd209", "0x512", "273"], "Ultimarc UltraStik Ultimarc UltraStik Player 2", "usb-0000:38:00.3-3.1.3/input1", "1"),
            DeviceMock("/dev/input/event15", ["BUS_USB", "0xd209", "0x512", "273"], "Ultimarc UltraStik Ultimarc UltraStik Player 2", "usb-0000:38:00.3-3.1.3/input2", "1")
        ]






