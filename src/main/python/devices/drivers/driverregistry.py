from devices.drivers.xbx360 import Xbox360
from devices.drivers.mouse import VirtualMouse
from devices.drivers.keybd import VirtualKeyboard


DEV_TYPES = {
    "xbx360": Xbox360,
    "keybd": VirtualKeyboard,
    "mouse": VirtualMouse
}
