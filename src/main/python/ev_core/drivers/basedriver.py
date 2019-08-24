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
        self.periodic_events = dict()

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

        if periodical == 0:
            self.input_dev.write(e_type, int(e_sub_type), value)
            return self

        # Autotrigger
        elif periodical > 0 and value == 1:
            if len(self.periodic_events) == 0:
                asyncio.ensure_future(self._loop_periodical())
            elif e_sub_type in self.periodic_events:
                return
            self._register_autotrigger(e_sub_type, e_type, frequency, value)
            self.input_dev.write(e_type, int(e_sub_type), value)

        elif periodical > 0 and value > 1 and e_sub_type in self.periodic_events:
            return

        else:
            self._deregister_auto_trigger(e_sub_type)
            self.input_dev.write(e_type, int(e_sub_type), value)

        return self

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
        while len(self.periodic_events) > 0:
            await asyncio.sleep(100e-3)
            try:
                for key in self.periodic_events:
                    now = datetime.now().microsecond
                    val = self.periodic_events[key]
                    if round(abs(now - val["last_accessed"]) / 1000) > val["frequency"]:
                        val["last_accessed"] = now
                        val["trigger"]()
                        await asyncio.sleep(100e-3)
                        val["trigger_off"]()
            # we would get somtimes a collection changed exception, we safely can ignore that
            # (race condition due to external delete and await in the loop
            except Exception as e:
                pass

    def _deregister_auto_trigger(self, e_sub_type):
        del self.periodic_events[e_sub_type]

    def _register_autotrigger(self, e_sub_type, e_type, frequency, value):
        # register autofire
        self.periodic_events[e_sub_type] = dict()
        self.periodic_events[e_sub_type]["frequency"] = frequency
        self.periodic_events[e_sub_type]["trigger"] = lambda: self._trigger(e_type, e_sub_type, value)
        self.periodic_events[e_sub_type]["trigger_off"] = lambda: self._trigger_off(e_type, e_sub_type, value)
        self.periodic_events[e_sub_type]["last_accessed"] = datetime.now().microsecond

    # a trigger function to be reused as a lambda for the autofire
    def _trigger(self, e_type, e_sub_type, value):
        self.input_dev.write(e_type, int(e_sub_type), value)
        self.syn()

    def _trigger_off(self, e_type, e_sub_type, value):
        self.input_dev.write(e_type, int(e_sub_type), 0)
        self.syn()
