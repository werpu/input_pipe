import pyudev
from ev_core.event_loop import EventController
from utils.langutils import *
from time import sleep


class UdevListener:

    def __init__(self, ev_ctl: EventController):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by("input")
        self.config = ev_ctl.config
        self.ev_ctl = ev_ctl
        self.restarting = False
        self.observer = pyudev.MonitorObserver(monitor, self.event_handler)
        self.observer.start()

    def event_handler(self, action, device):
        name = device.get("ID_VENDOR") + " " + device.get("ID_MODEL")
        name = name.replace("_", " ")
        found = True
        for input_key in self.config.inputs:
            c_name, name_re, phys, phys_re, rel_pos, vendor, product, exclusive = \
                self.config.get_config_input_params(input_key)

            if c_name is not None:
                found = found or caseless_equal(name, c_name)
            elif name_re is not None:
                found = found or re_match(name, name_re)

            if found:
                break

        if found and action == "add":
            if self.restarting:
                return
            self.restarting = True
            sleep(3)
            self.ev_ctl.restart()
            self.restarting = False
        elif found and action == "remove":
            self.ev_ctl.stop()
