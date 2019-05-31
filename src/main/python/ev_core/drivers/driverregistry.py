from ev_core.drivers.xbx360 import Xbox360
from ev_core.drivers.mouse import VirtualMouse
from ev_core.drivers.keybd import VirtualKeyboard


DEV_TYPES = {
    "xbx360": Xbox360,
    "keybd": VirtualKeyboard,
    "mouse": VirtualMouse
}
