# @see:https://python-evdev.readthedocs.io/en/latest/tutorial.html#create-uinput-device-with-capabilities-of-another-device
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

from evdev import ecodes, AbsInfo
from ev_core.drivers.basedriver import BaseDriver


# todo check with a real xbox controller
class Xbox360(BaseDriver):

    _init_cnt = 0

    def __init__(self):
        BaseDriver.__init__(self)

        self.input_dev = None
        self.create_node = True
        self.bustype = "BUS_USB"
        self.name = "Microsoft X-Box 360 pad"
        self.vendor = 0x45e
        self.product = 0x28e
        self.version = 272
        self.phys = "joydrv/virtpad" + Xbox360._init_cnt.__str__()
        self.bits_ev = "(null) (null) (null)"

        Xbox360._init_cnt += 1

        self.capabilities = {
            ecodes.EV_KEY: [
                ecodes.BTN_A,
                ecodes.BTN_B,
                ecodes.BTN_X,
                ecodes.BTN_Y,
                ecodes.BTN_TL,
                ecodes.BTN_TR,
                ecodes.BTN_TL2,
                ecodes.BTN_TR2,
                ecodes.BTN_SELECT,
                ecodes.BTN_START,
                ecodes.BTN_THUMBL,
                ecodes.BTN_THUMBR,
                ecodes.BTN_DPAD_UP,
                ecodes.BTN_DPAD_DOWN,
                ecodes.BTN_DPAD_LEFT,
                ecodes.BTN_DPAD_RIGHT,
                ecodes.BTN_MODE,
            ],
            ecodes.EV_ABS: [
                (ecodes.ABS_HAT0X, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                (ecodes.ABS_HAT0Y, AbsInfo(value=0, min=-1, max=1, fuzz=0, flat=0, resolution=0)),
                (ecodes.ABS_X, AbsInfo(value=128, min=0, max=255, fuzz=15, flat=0, resolution=0)),
                (ecodes.ABS_Y, AbsInfo(value=128, min=0, max=255, fuzz=15, flat=0, resolution=0)),
                (ecodes.ABS_RX, AbsInfo(value=128, min=0, max=255, fuzz=15, flat=0, resolution=0)),
                (ecodes.ABS_RY, AbsInfo(value=128, min=0, max=255, fuzz=15, flat=0, resolution=0))
            ]
        }

    def close(self):
        BaseDriver.close(self)
        Xbox360._init_cnt -= 1
