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

from abc import ABC, abstractmethod

from evdev import UInput


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

    def create(self):
        self.input_dev = UInput(self.capabilities,
                                self.name,
                                vendor=self.vendor,
                                product=self.product,
                                version=self.version,
                                phys=self.phys)

        return self

    def write(self, e_type, e_sub_type, value):
        self.input_dev.write(e_type, e_sub_type, value)
        return self

    def syn(self):
        self.input_dev.syn()
        return self

    def verify(self):
        self.input_dev.verify()
        return self

    def transfer_dev_data(self):
        self.phys = self.input_dev.phys
        self.name = self.input_dev.name
        self.version = self.input_dev.version
        self.vendor = self.input_dev.vendor
        self.bustype = self.input_dev.bustype
        self.product = self.input_dev.product
