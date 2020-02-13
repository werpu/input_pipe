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

import os
import stat
import time
from time import sleep

from evdev import UInput, ecodes, AbsInfo
from ev_core.drivers.basedriver import BaseDriver


class VirtualMouse(BaseDriver):

    _init_cnt = 0

    def __init__(self):
        BaseDriver.__init__(self)

        self.phys = "joydrv/virtmouse" + VirtualMouse._init_cnt.__str__()
        self.name = "virtual-mouse"

        VirtualMouse._init_cnt += 1

        self.capabilities = {
            ecodes.EV_REL: (ecodes.REL_X, ecodes.REL_Y),
            ecodes.EV_KEY: (ecodes.BTN_LEFT, ecodes.BTN_MIDDLE, ecodes.BTN_RIGHT)
        }

    def create(self, meta=None):

        self.input_dev = UInput(self.capabilities,
                                self.name,
                                phys=self.phys)
        self.transfer_dev_data()

        return self

    def close(self):
        BaseDriver.close(self)
        VirtualMouse._init_cnt -= 1

    # helpers for the exec macros
    def press_btn_middle(self):
        self.write(None, None, ecodes.EV_KEY, ecodes.BTN_MIDDLE, 1)
        self.syn()
        time.sleep(100e-3)
        self.write(None, None, ecodes.EV_KEY, ecodes.BTN_MIDDLE, 0)
        self.syn()

    def press_btn_left(self):
        self.write(None, None, ecodes.EV_KEY, ecodes.BTN_LEFT, 1)
        self.syn()
        time.sleep(100e-3)
        self.write(None, None, ecodes.EV_KEY, ecodes.BTN_LEFT, 0)
        self.syn()

    def press_btn_right(self):
        self.write(None, None, ecodes.EV_KEY, ecodes.BTN_RIGHT, 1)
        self.syn()
        time.sleep(100e-3)
        self.write(None, None, ecodes.EV_KEY, ecodes.BTN_RIGHT, 0)
        self.syn()

    def move(self, rel_x, rel_y):
        self.write(None, None, ecodes.EV_REL, ecodes.REL_X, rel_x)
        self.write(None, None, ecodes.EV_REL, ecodes.REL_Y, rel_y)
        self.syn()

