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
