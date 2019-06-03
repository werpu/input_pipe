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
                                self.name,
                                phys=self.phys)
        self.transfer_dev_data()

        return self
