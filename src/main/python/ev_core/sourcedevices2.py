import asyncio
from time import sleep

import evdev
import pyinotify

from ev_core.config import Config
from utils.evdevutils import EvDevUtils
from utils.langutils import *


class EventHandler(pyinotify.ProcessEvent):
    """
    This is the central core ouf our hotplugging
    we basically use the linux input event system
    to detect whether all needed devices
    are plugged in and stop and/or shut our engine down until this state is reached or
    whenever this state is broken see also

    https://www.saltycrane.com/blog/2010/04/monitoring-filesystem-python-and-pyinotify/
    https://github.com/gvalkov/python-evdev/issues/99

    Thanks for everyone on the net for gathering this info
    """

    def __init__(self, config: Config, get_available_devices:callable=None, pevent=None, **kargs):
        super().__init__(pevent, **kargs)
        self._get_available_devices = get_available_devices
        self.devices = []
        self.matched = {}
        self.matched_paths = {}
        self._matched_devices = {}
        self.config = config
        self.all = False
        self.init_if_plugged_in()

    def reset(self):
        self.devices = []
        self.matched = {}
        self.matched_paths = {}
        self._matched_devices = {}

    def init_if_plugged_in(self):
        if self.all:
            return
        print("scanning for source devices")

        # wait 2 seconds for the nodes to catch up
        # sometimes some subdevices need a little bit of time
        # to have their nodes created
        sleep(2)
        devices = self.get_available_devices()

        for device in devices:
            self.handle_match(device, device.path)

    """
    Gets all available devices
    which are bound to the evdev api from linux
    """
    def get_available_devices(self):
        if self._get_available_devices is not None:
            devices = self._get_available_devices()
        else:
            devices = EvDevUtils.get_available_devices()

        devices.sort(key=lambda dev: save_fetch(lambda: dev.fd, "-"), reverse=True)
        return devices

    """
    event handler for the creation function
    every time a node is created it is matched
    against our matcher to see whether a new
    usable device was plugged in which can
    be processed by our rules engine
    """
    def process_IN_CREATE(self, event):
        if self.all or event.dir or not event.name.startswith("event"):
            return

        asyncio.ensure_future(self.match_device2())

    async def match_device2(self):
        await asyncio.sleep(2)
        self.init_if_plugged_in()

    async def match_device(self, event):
        # we have to retry until the device is unlocked by the generation event
        # after 10 tries we give up
        save_call(lambda: self.event_match(event))

    def event_match(self, event):
        dev = evdev.InputDevice(event.pathname)
        self.handle_match(dev, event.pathname)

    """
    Match processing method
    matches a device against our device
    rules configuration 
    """
    def handle_match(self, dev, pathname):
        matched, input_dev_key = self._device_match(dev)
        if matched:
            self.matched_paths[pathname] = True
            dev.__dict__["_input_dev_key_"] = input_dev_key
            self.devices.append(dev)
            print("  - " + dev.name + " found ")
            if len(self.devices) == len(self.config.inputs):
                print("all devices found")
                self.all = True
                print("Following devices were found:")
                for device in self.devices:
                    print("  - " + device.name)
                self.config.event_emitter.emit("handler_start")

    """
    handle delete, whenever a matched device is unplugged we need to shut the system entirely down
    and wait until all the matched devices are plugged back in
    for the time being it is an all or nothing approach
    """
    def process_IN_DELETE(self, event):
        if event.dir:
            return
        if not event.name.startswith("event"):
            return
        if event.pathname not in self.matched_paths:
            return
        if self.all:
            asyncio.ensure_future(self.cleanup())

    async def cleanup(self):
        # again we wait a little bit so that
        # all nodes are unlocked after the linux event
        await asyncio.sleep(0.5)
        self.config.event_emitter.emit("handler_stop")
        self.all = False
        self.matched = {}
        self.matched_paths = {}
        self._matched_devices = {}

    """
    Complex device match, it basically first
    checks for a full name or phys match
    and if not found tries a re match for name or phys
    also takes the rel device position into consideration
    which is the relativ device in multiple matches
    """
    def _device_match(self, device: evdev.InputDevice):
        for key in save_fetch(lambda: self.config.inputs, {}):
            name, name_re, phys, phys_re, rel_pos, vendor, product, exclusive, i_max, i_min, i_deadzone = self.config.get_config_input_params(key)

            device_match_string = str(self.config.inputs[key])

            found = Config.full_match(device, name, name_re, phys, phys_re, vendor, product)

            if found:
                if exclusive:
                    try:
                        device.grab()
                    except Exception as e:
                        print(e)
                        pass
                if save_fetch(lambda: self._matched_devices[device_match_string], False) is True:
                    return False, None
                accessor_key = name or phys or name_re or phys_re or vendor or product
                already_processed = save_fetch(lambda: self.matched[accessor_key], 1)
                if already_processed == rel_pos:
                    self._matched_devices[device_match_string] = True
                    return True, key
                else:
                    self.matched[accessor_key] = already_processed + 1
        return False, None


class SourceDevices2:
    """
    A device holder class
    determines the devices in the input devices
    section and then stores the ones which match from
    the inputs section of the config
    """

    def __init__(self, config: Config):
        self.watch_manager = pyinotify.WatchManager()
        self.loop = asyncio.get_event_loop()
        # first we need to initially search
        self.handler = EventHandler(config, self.get_available_devices)
        # second we start an internal watchdog for hotplugging
        self.notifier = pyinotify.AsyncioNotifier(self.watch_manager, self.loop, default_proc_fun=self.handler)
        self.watch_manager.add_watch('/dev/input',
                                     pyinotify.IN_CREATE |
                                     pyinotify.IN_DELETE,
                                     rec=True, auto_add=True)

        # unless all devices are checked in we do not process any further with the basic initialisation
        ## asyncio.set_event_loop(self.loop)
        ##asyncio.run(self.awaiter())

    def get_available_devices(self):
        devices = EvDevUtils.get_available_devices()

        devices.sort(key=lambda dev: save_fetch(lambda: dev.fd, "-"), reverse=True)
        return devices

    async def awaiter(self):
        while not self.handler.all:
            await asyncio.sleep(3)

    @property
    def all_found(self):
        return self.handler.all

    @property
    def devices(self):
        return self.handler.devices

    def close(self):
        for device in self.devices:
            try:
                device.ungrab()
            except Exception as e:
                pass
            device.close()
        self.handler.reset()

