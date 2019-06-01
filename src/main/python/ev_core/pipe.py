from test_utils.sourceDevicesMock import SourceDevicesMock
from ev_core.targetdevices import TargetDevices
from ev_core.eventtree import EventTree
from ev_core.config import Config
import asyncio
from evdev import ecodes, AbsInfo
from evdev.events import KeyEvent, AbsEvent, RelEvent, InputEvent, SynEvent
from utils.langutils import *


#
# the central pipe which reacts on events from ther source devices
# and maps them into proper events in the target devices
# this is sort of the central controller, which controls
# code based on
# https://python-evdev.readthedocs.io/en/latest/tutorial.html#reading-events-from-multiple-devices-using-asyncio
#
class EvDevPipe:

    def __init__(self, config: Config):
        self.source_devices = SourceDevicesMock(config)
        self.target_devices = TargetDevices(config)
        self.event_tree = EventTree(config, self.source_devices, self.target_devices)

        for src_dev in self.source_devices.devices:
            asyncio.ensure_future(self.handle_events(src_dev))

        loop = asyncio.get_event_loop()
        loop.run_forever()

    def handle_events(self, src_dev):
        async for event in src_dev.async_read_loop():
            self.resolve_event( event)

    def resolve_event(self, event):

        root_type = self.map_type(event)

        target_rules = save_fetch(lambda: self.event_tree.tree[root_type][event.code], {})
        for key in target_rules:
            target_event = target_rules[key]
            target_type = target_event["ev_type"]
            target_code = target_event["ev_code"]
            target_value = event.value
            target_device = target_event["driver"]
            # todo write event data
            target_device.write(ecodes[target_type], target_code, event.value)

    def map_type(self, event):
        root_type = None
        if isinstance(event, KeyEvent):
            root_type = "EV_KEY"
        elif isinstance(event, AbsEvent):
            root_type = "EV_ABS"
        elif isinstance(event, RelEvent):
            root_type = "EV_REL"

        return root_type
