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

from evdev import UInput, ecodes
from ev_core.drivers.basedriver import BaseDriver


class VirtualKeyboard(BaseDriver):

    def __init__(self):
        BaseDriver.__init__(self)
        self.name = "virtual-keyboard"
        self.capabilities = {
            ecodes.EV_KEY: [
                ecodes.KEY_0,
                ecodes.KEY_1,
                ecodes.KEY_2,
                ecodes.KEY_3,
                ecodes.KEY_4,
                ecodes.KEY_5,
                ecodes.KEY_6,
                ecodes.KEY_7,
                ecodes.KEY_8,
                ecodes.KEY_9,
                ecodes.KEY_0,
                ecodes.KEY_A,
                ecodes.KEY_B,
                ecodes.KEY_C,
                ecodes.KEY_D,
                ecodes.KEY_E,
                ecodes.KEY_F,
                ecodes.KEY_G,
                ecodes.KEY_H,
                ecodes.KEY_I,
                ecodes.KEY_J,
                ecodes.KEY_K,
                ecodes.KEY_L,
                ecodes.KEY_M,
                ecodes.KEY_N,
                ecodes.KEY_O,
                ecodes.KEY_P,
                ecodes.KEY_Q,
                ecodes.KEY_R,
                ecodes.KEY_S,
                ecodes.KEY_T,
                ecodes.KEY_U,
                ecodes.KEY_V,
                ecodes.KEY_W,
                ecodes.KEY_X,
                ecodes.KEY_Y,
                ecodes.KEY_Z,
                ecodes.KEY_F1,
                ecodes.KEY_F2,
                ecodes.KEY_F3,
                ecodes.KEY_F4,
                ecodes.KEY_F5,
                ecodes.KEY_F6,
                ecodes.KEY_F7,
                ecodes.KEY_F8,
                ecodes.KEY_F9,
                ecodes.KEY_F10,
                ecodes.KEY_F11,
                ecodes.KEY_F12,
                ecodes.KEY_UP,
                ecodes.KEY_DOWN,
                ecodes.KEY_LEFT,
                ecodes.KEY_RIGHT,
                ecodes.KEY_ENTER,
                ecodes.KEY_END,
                ecodes.KEY_ESC,
                ecodes.KEY_DELETE,
                ecodes.KEY_LEFTALT,
                ecodes.KEY_LEFTMETA,
                ecodes.KEY_RIGHTALT,
                ecodes.KEY_RIGHTMETA,
                ecodes.KEY_LEFTSHIFT,
                ecodes.KEY_RIGHTSHIFT,
                ecodes.KEY_CAPSLOCK,
                ecodes.KEY_NUMERIC_0,
                ecodes.KEY_NUMERIC_1,
                ecodes.KEY_NUMERIC_2,
                ecodes.KEY_NUMERIC_3,
                ecodes.KEY_NUMERIC_4,
                ecodes.KEY_NUMERIC_5,
                ecodes.KEY_NUMERIC_7,
                ecodes.KEY_NUMERIC_8,
                ecodes.KEY_NUMERIC_9,
                ecodes.KEY_NUMERIC_0
            ]
        }

    def create(self):
        self.input_dev = UInput(self.capabilities,
                                self.name)
        self.transfer_dev_data()
        return self
