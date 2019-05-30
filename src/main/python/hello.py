# https://python-evdev.readthedocs.io/en/latest/usage.html


# import pyudev

# context = pyudev.Context()
# monitor = pyudev.Monitor.from_netlink(context)
# monitor.filter_by(subsystem='usb')

# for device in iter(monitor.poll, None):
#    if device.action == 'add':
#        print('{} connected'.format(device))

import evdev
from utils.sourcedevices import SourceDevices
from utils.config import Config

deviceList = SourceDevices()

conf = Config()
print(conf.inputs)
print(conf.__dict__)


for device in deviceList.devices:
    devPath = device.path
    devName = device.name
    phys = device.phys

    print(devPath, devName, phys)
