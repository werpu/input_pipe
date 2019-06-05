import pyudev

from utils.langutils import *
from time import sleep

# Udev hotplugging listener
# the idea is to simulate udev rules with this one
# whenever one of our source devices is removed we need to shutdown
# the pipe and whenever it is attached
# we reactivate the pipe and target inputs
# it is an all or nothing approach
# partial piping is not yet supported
class UdevListener:

    def __init__(self, ev_ctl):
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by("usb")

        monitor2 = pyudev.Monitor.from_netlink(context)
        monitor2.filter_by("input")

        self.config = ev_ctl.config
        self.ev_ctl = ev_ctl
        self.restarting = False
        self.observer = pyudev.MonitorObserver(monitor, self._usb_event_handler)
        self.observer2 = pyudev.MonitorObserver(monitor, self._input_event_handler)
        self.observer.start()
        self.observer2.start()

    # id vendor only on input level detectable in the remove case
    def _usb_event_handler(self, action, device):
        found, name = self._get_udev_base_data(device)
        found = self._match_udev_data(found, name)

        if found and action == "remove":
            self.ev_ctl.stop()

    # in the add case we can savely work only on usb level
    # because doing that over input would put us into an endless
    # loop
    def _input_event_handler(self, action, device):
        found, name = self._get_udev_base_data(device)
        found = self._match_udev_data(found, name)

        if found and action == "add":
            if self.restarting:
                return
            self.restarting = True
            sleep(5)
            self.ev_ctl.restart()
            self.restarting = False

    def _match_udev_data(self, found, name, vendor=None):
        for input_key in self.config.inputs:
            c_name, name_re, phys, phys_re, rel_pos, c_vendor, product, exclusive = \
                self.config.get_config_input_params(input_key)

            if c_name is not None:
                found = found or caseless_equal(name, c_name)
            # elif vendor is not None:
            #    found = found or caseless_equal("0x"+vendor, c_vendor)
            elif name_re is not None:
                found = found or re_match(name, name_re)

            if found:
                break
        return found

    @staticmethod
    def _get_udev_base_data(device):
        name = (device.get("ID_VENDOR") or "____") + " " + (device.get("ID_MODEL") or "____")
        name = name.replace("_", " ")
        found = True
        return found, name
