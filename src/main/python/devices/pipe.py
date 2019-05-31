from test_utils.sourceDevicesMock import SourceDevicesMock
from devices.targetdevices import TargetDevices
from devices.eventtree import EventTree
from utils.config import Config
from utils.langutils import *


class EvDevPipe:

    def __init__(self, config: Config):
        self.source_devices = SourceDevicesMock(config)
        self.target_devices = TargetDevices(config)
        self.event_tree = EventTree(config, self.source_devices, self.target_devices)

