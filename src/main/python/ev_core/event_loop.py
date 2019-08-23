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
import asyncio

from evdev import ecodes
from evdev.events import KeyEvent, AbsEvent, RelEvent

from ev_core.config import Config
from ev_core.eventtree import EventTree, EV_CODE, EV_META, EV_TYPE, DRIVER, EV_PERIODICAL, EV_FREQUENCY
from ev_core.sourcedevices import SourceDevices
from ev_core.targetdevices import TargetDevices
from ev_core.udevlistener import UdevListener
from utils.langutils import *


# from circuits import Component, handler


#
# the central controller pipe which reacts on events from their source devices
# and maps them into proper events in the target devices
# this is sort of the central controller, which controls
# code based on
# https://python-evdev.readthedocs.io/en/latest/tutorial.html#reading-events-from-multiple-devices-using-asyncio
#
class EventController:

    def __init__(self, config: Config):
        self.config = config
        self.futures = []
        self.source_devices = None
        self.target_devices = None
        self.event_tree = None
        self.loop = None
        self.running_controller = False
        self.udev_listener = UdevListener(self)
        self.touched = {}
        self.start()

    # starts the event loop internally
    def start(self):
        if self.running_controller:
            return
        self.running_controller = True
        print("scanning for source devices")
        self.source_devices = SourceDevices(self.config)
        print("creating target devices")
        self.target_devices = TargetDevices(self.config)
        self.event_tree = EventTree(self.config, self.source_devices, self.target_devices)
        self.futures = []
        for src_dev in self.source_devices.devices:
            self.futures.append(asyncio.ensure_future(self.handle_events(src_dev)))

    # stops the event loop internally
    def stop(self):
        if not self.running_controller:
            return
        print("stopping event loop")
        self.running_controller = False
        asyncio.set_event_loop(self.loop)
        for future in self.futures:
            future.cancel()
        self.target_devices.close()
        self.source_devices = None

    def reload(self):
        self.stop()
        self.start()

    # update data, allows to change event confgurations on the fly
    def update_data(self, new_config):
        print("rewiring event cofiguration")
        self.config = new_config
        self.event_tree = EventTree(self.config, self.source_devices, self.target_devices)

    async def handle_events(self, src_dev):
        async for event in src_dev.async_read_loop():
            try:
                self.resolve_event(event, src_dev)
            except Exception as e:
                print(e)
                pass

    def resolve_event(self, event, src_dev):
        # analog deadzone
        if 113 <= event.value <= 143:
            return

        root_type = self.map_type(event)
        if root_type is None:
            return

        source_device = src_dev.__dict__["_input_dev_key_"]
        target_rules = save_fetch(lambda: self.event_tree.tree[source_device][root_type][str(event.code)], {})

        if event.type == ecodes.EV_SYN:
            for phys_device in self.touched:
                self.touched[phys_device].syn()
            self.touched.clear()

        for key in target_rules:
            target_code, target_device, target_type, target_value, target_meta, periodical, frequency = self.get_target_data(event, key,
                                                                                                      target_rules)
            target_device.write(self.config, self.target_devices.drivers or {},
                                save_fetch(lambda: ecodes.__getattribute__(target_type), -1), target_code, target_value,
                                target_meta, periodical, frequency)
            self.touched[target_device.phys] = target_device

    @staticmethod
    def get_target_data(event, key, target_rules):
        target_event = target_rules[key]
        target_type = target_event[EV_TYPE] or None
        target_code = target_event[EV_CODE] or None
        target_value = save_fetch(lambda: int(target_event["value"]), event.value) if abs(event.value) > 0 else \
            event.value
        target_device = target_event[DRIVER]
        target_meta = target_event[EV_META] or None
        periodical = target_event[EV_PERIODICAL]
        freqency = target_event[EV_FREQUENCY]
        return target_code, target_device, target_type, target_value, target_meta, periodical, freqency

    @staticmethod
    def map_type(event):
        root_type = None
        if event.type == 0:
            root_type = "EV_SYN"
        elif event.type == 1:
            root_type = "EV_KEY"
        elif event.type == 2:
            root_type = "EV_REL"
        elif event.type == 3:
            root_type = "EV_ABS"
        elif event.type == 4:
            root_type = "EV_MSC"
        elif isinstance(event, KeyEvent):
            root_type = "EV_KEY"
        elif isinstance(event, AbsEvent):
            root_type = "EV_ABS"
        elif isinstance(event, RelEvent):
            root_type = "EV_REL"

        return root_type
