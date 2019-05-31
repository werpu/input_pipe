# @see:https://python-evdev.readthedocs.io/en/latest/tutorial.html#create-uinput-device-with-capabilities-of-another-device

from evdev import ecodes, AbsInfo
from devices.drivers.basedriver import BaseDriver


# todo check with a real xbox controller
class Xbox360(BaseDriver):

    _init_cnt = 0

    def __init__(self):
        BaseDriver.__init__(self)

        self.input_dev = None
        self.create_node = True
        self.bustype = "BUS_USB"
        self.name = "Microsoft X-Box 360 pad"
        self.vendor = 0x45e
        self.product = 0x28e
        self.version = 272
        self.phys = "joydrv/virtpad" + Xbox360._init_cnt.__str__()
        self.bits_ev = "(null) (null) (null)"

        Xbox360._init_cnt += 1

        self.capabilities = {
            ecodes.EV_KEY: [
                ecodes.BTN_A,
                ecodes.BTN_B,
                ecodes.BTN_X,
                ecodes.BTN_Y,
                ecodes.BTN_TL,
                ecodes.BTN_TR,
                ecodes.BTN_TL2,
                ecodes.BTN_TR2,
                ecodes.BTN_SELECT,
                ecodes.BTN_START,
                ecodes.BTN_THUMBL,
                ecodes.BTN_THUMBR,
                ecodes.BTN_DPAD_UP,
                ecodes.BTN_DPAD_DOWN,
                ecodes.BTN_DPAD_LEFT,
                ecodes.BTN_DPAD_RIGHT,
                ecodes.BTN_MODE,
            ],
            ecodes.EV_ABS: [
                (ecodes.ABS_X, AbsInfo(value=0, min=0, max=255, fuzz=15, flat=0, resolution=0)),
                (ecodes.ABS_Y, AbsInfo(value=0, min=0, max=255, fuzz=15, flat=0, resolution=0)),
                (ecodes.ABS_RX, AbsInfo(value=0, min=0, max=255, fuzz=15, flat=0, resolution=0)),
                (ecodes.ABS_RY, AbsInfo(value=0, min=0, max=255, fuzz=15, flat=0, resolution=0))
            ]
        }
