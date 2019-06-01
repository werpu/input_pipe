# https://python-evdev.readthedocs.io/en/latest/usage.html


from ev_core.config import Config
from ev_core.pipe import EvDevPipe

EvDevPipe(Config("../resources/devices.yaml"))

