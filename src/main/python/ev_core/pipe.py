from test_utils.sourceDevicesMock import SourceDevicesMock
from ev_core.targetdevices import TargetDevices
from ev_core.eventtree import EventTree
from ev_core.config import Config


class EvDevPipe:

    def __init__(self, config: Config):
        self.source_devices = SourceDevicesMock(config)
        self.target_devices = TargetDevices(config)
        self.event_tree = EventTree(config, self.source_devices, self.target_devices)

