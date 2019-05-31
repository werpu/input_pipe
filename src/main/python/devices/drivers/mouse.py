import os
import stat
from time import sleep

from evdev import UInput, ecodes, AbsInfo
from devices.drivers.basedriver import BaseDriver


class VirtualMouse(BaseDriver):

    def __init__(self):
        BaseDriver.__init__(self)
        self.name = "virtual-mouse"
        self.capabilities = {
            ecodes.EV_KEY: [
                ecodes.BTN_LEFT,
                ecodes.BTN_MIDDLE,
                ecodes.BTN_RIGHT,
                ecodes.BTN_MOUSE
            ],
            ecodes.EV_ABS: [
                (ecodes.ABS_X, AbsInfo(value=0, min=0, max=255, fuzz=0, flat=0, resolution=0)),
                (ecodes.ABS_Y, AbsInfo(0, 0, 255, 0, 0, 0)),
                (ecodes.ABS_MT_POSITION_X, (0, 128, 255, 0))]
        }

    def create(self):

        self.input_dev = UInput(self.capabilities,
                                self.name)
        self.transfer_dev_data()

        return self
