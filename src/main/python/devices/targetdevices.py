# https://python-evdev.readthedocs.io/en/latest/usage.html
import evdev
from utils.config import Config, PHYS_RE, NAME_RE, PHYS, NAME, RELPOS, VENDOR, PRODUCT, INFO
from utils.langutils import *
from devices.drivers.driverregistry import DEV_TYPES


class TargetDevices:

    def __init__(self, config: Config):

        self.config = config
        self.drivers = {}

        for key in config.outputs:
            dev_key, dev_name, dev_type = self.get_config_data(key)

            driver = tree_fetch(DEV_TYPES[dev_type](), None)

            if driver is not None:
                self.drivers[dev_key] = driver
                print("Output driver found for "+dev_key)

    # Fetches the associated config data
    def get_config_data(self, key):
        dev_key = key
        dev_name = tree_fetch(lambda: self.config.outputs[key][NAME], None)
        dev_type = tree_fetch(lambda: self.config.outputs[key]["type"], None)

        return dev_key, dev_name, dev_type

