from utils.devices import Devices
from utils.config import Config
from test_utils.deviceMock import DeviceMock


class DevicesMock(Devices):

    def __init__(self, config: Config):
        Devices.__init__(self, config)

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






