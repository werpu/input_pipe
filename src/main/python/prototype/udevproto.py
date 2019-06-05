import pyudev

#class UdevListener:
from asyncio import sleep


def event_handler(action, device):
    print(device.get("ID_VENDOR") + " " + device.get("ID_MODEL"))


context = pyudev.Context()
monitor = pyudev.Monitor.from_netlink(context)
monitor.filter_by("input")
observer = pyudev.MonitorObserver(monitor, event_handler)
observer.start()

while True:
    sleep(5)

