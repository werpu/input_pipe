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
from datetime import datetime
from abc import ABC, abstractmethod
from evdev import UInput
from ev_core.config import Config

# CONSTANTS used by this file
STD_DELAY = 100e-3
LAST_ACCESSED = "last_accessed"
TRIGGER = "trigger"
FREQUENCY = "frequency"
TRIGGER_OFF = "trigger_off"


###################################################################################
# Base Driver, this is the base for all our drivers
# it implements the basic driver mechanisms and provides various helpers
# Also it implements the device event forwarding and auto trigger/fire mechanisms
###################################################################################
class BaseDriver(ABC):

    @abstractmethod
    def __init__(self):
        self.create_node = True
        self.name = None
        self.input_dev = None
        self.capabilities = None
        self.vendor = None
        self.product = None
        self.version = None
        self.phys = None
        self.bustype = None
        self.auto_triggers = dict()

    def create(self):
        self.input_dev = UInput(self.capabilities,
                                self.name,
                                vendor=self.vendor,
                                product=self.product,
                                version=self.version,
                                phys=self.phys)

        return self

    # Central write handler
    # handles all kind of writes, single writes and auto triggers
    def write(self, config: Config, drivers, e_type=None, e_sub_type=None, value=None, meta=None, periodical=0, frequency=0):

        auto_trigger_button_pressed, auto_trigger_button_released, auto_trigger_button_toggle, auto_trigger_press_ongoing, no_auto_trigger = self._calculate_toggle_state(
            e_sub_type, periodical, value)

        # Normal state first which is 90% of all triggers hence needs to be processed first
        if no_auto_trigger:
            self.input_dev.write(e_type, int(e_sub_type), value)
            return self

        # Autotrigger states
        elif auto_trigger_button_pressed:
            if len(self.auto_triggers) == 0:
                asyncio.ensure_future(self._loop_periodical())
            elif e_sub_type in self.auto_triggers:
                return self
            self._register_auto_trigger(e_sub_type, e_type, frequency, value)
            self.input_dev.write(e_type, int(e_sub_type), value)

        elif auto_trigger_press_ongoing:
            return self

        elif auto_trigger_button_released:
            self._deregister_auto_trigger(e_sub_type)
            self.input_dev.write(e_type, int(e_sub_type), value)

        elif auto_trigger_button_toggle:
            self._toggle_auto_trigger(e_sub_type, e_type, frequency, value)

        else:
            self.input_dev.write(e_type, int(e_sub_type), value)

        return self

    # calculate the toggle states for the auto fire function
    def _calculate_toggle_state(self, e_sub_type, periodical, value):
        no_auto_trigger = periodical == 0
        auto_trigger_button_pressed = periodical == 1 and value == 1
        auto_trigger_button_released = periodical == 1 and value == 0
        auto_trigger_press_ongoing = periodical == 1 and value > 1 and e_sub_type in self.auto_triggers
        auto_trigger_button_toggle = periodical == 2 and value == 1
        return auto_trigger_button_pressed, auto_trigger_button_released, auto_trigger_button_toggle, auto_trigger_press_ongoing, no_auto_trigger

    def syn(self):
        self.input_dev.syn()
        return self

    def verify(self):
        self.input_dev.verify()
        return self

    def close(self):
        if self.input_dev is not None:
            self.input_dev.close()

    def transfer_dev_data(self):
        self.phys = self.input_dev.phys
        self.name = self.input_dev.name
        self.version = self.input_dev.version
        self.vendor = self.input_dev.vendor
        self.bustype = self.input_dev.bustype
        self.product = self.input_dev.product

    # periodic loop which triggers the autofire
    async def _loop_periodical(self):
        while len(self.auto_triggers) > 0:
            await asyncio.sleep(STD_DELAY)
            try:
                for key in self.auto_triggers:
                    now = datetime.now().microsecond
                    val = self.auto_triggers[key]
                    access_difference = round(abs(now - val[LAST_ACCESSED]) / 1000)
                    if access_difference > val[FREQUENCY]:
                        val[LAST_ACCESSED] = now
                        val[TRIGGER]()
                        # 100ms delay because some emulators do not accept input which is lower than that
                        # between button up and button down
                        await asyncio.sleep(STD_DELAY)
                        val[TRIGGER_OFF]()
            # we would get somtimes a collection changed exception, we safely can ignore that
            # (race condition due to external delete and await in the loop
            except Exception as e:
                pass

    def _deregister_auto_trigger(self, e_sub_type):
        del self.auto_triggers[e_sub_type]

    # registers an auto trigger into our trigger dictionary
    def _register_auto_trigger(self, e_sub_type, e_type, frequency, value):
        self.auto_triggers[e_sub_type] = dict()
        self.auto_triggers[e_sub_type][FREQUENCY] = frequency
        self.auto_triggers[e_sub_type][TRIGGER] = lambda: self._button_down(e_type, e_sub_type, value)
        self.auto_triggers[e_sub_type][TRIGGER_OFF] = lambda: self._button_up(e_type, e_sub_type, value)
        self.auto_triggers[e_sub_type][LAST_ACCESSED] = datetime.now().microsecond

    # simulates a button down
    def _button_down(self, e_type, e_sub_type, value):
        self.input_dev.write(e_type, int(e_sub_type), value)
        self.syn()

    # simulates a button up
    def _button_up(self, e_type, e_sub_type, value):
        self.input_dev.write(e_type, int(e_sub_type), 0)
        self.syn()

    # toggles the auto triggers either on or off
    def _toggle_auto_trigger(self, e_sub_type, e_type, frequency, value):
        if e_sub_type in self.auto_triggers:
            del self.auto_triggers[e_sub_type]
        else:
            self. _register_auto_trigger(e_sub_type, e_type, frequency, value)

