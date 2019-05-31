# https://python-evdev.readthedocs.io/en/latest/usage.html
from ev_core.config import Config, NAME
from utils.langutils import *
from ev_core.drivers.driverregistry import DEV_TYPES


class TargetDevices:

    def __init__(self, config: Config):

        self.config = config
        self.drivers = {}

        for key in config.outputs:
            dev_key, dev_name, dev_type = self.get_config_data(key)

            driver = save_fetch(lambda: DEV_TYPES[dev_type](), None)

            if driver is not None:
                self.drivers[dev_key] = driver
                print("Output driver found for "+dev_key)

    # Fetches the associated config data
    def get_config_data(self, key):
        dev_key = key
        dev_name = save_fetch(lambda: self.config.outputs[key][NAME], None)
        dev_type = save_fetch(lambda: self.config.outputs[key]["type"], None)

        return dev_key, dev_name, dev_type

