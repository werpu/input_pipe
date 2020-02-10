import serial as serial

from ev_core.config import Config
from ev_core.drivers.basedriver import BaseDriver
import os
import serial

JOY_0 = 0x0
JOY_1 = 0x1
KEYBD = 0x2
MOUSE = 0x3


# inputs
BTN_A = 0x1
BTN_B = 0x2
BTN_X = 0x3
BTN_Y = 0x4
BTN_L = 0x5
BTN_R = 0x6
BTN_LT = 0x7
BTN_RT = 0x8
BTN_SEL = 0x9
BTN_STRT = 0xA
BTN_HL = 0xB
BTN_HR = 0xC
BTN_HT = 0xD
BTN_HB = 0xE
BTN_LS = 0xF
BTN_RS = 0x10

AL_Y = 11
AL_X = 12
AR_Y = 13
AR_X = 14

class SerialDriver(BaseDriver):
    """
    Serial driver, for a UART connextion
    to an external board providing
    the joystick emulation to external devices
    """
    _init_cnt = 0
    port = "/dev/serial0"
    ser = None

    def __init__(self):
        self.phys = "serial" + SerialDriver._init_cnt.__str__()
        SerialDriver._init_cnt += 1
        self.name = "serial0"
        self.ser = serial.Serial('/dev/ttyS0', 9600)
        pass

    def create(self):
        pass

    def write(self, config: Config, drivers, e_type, e_sub_type, value, meta=None, periodical=0, frequency=0, event=None):
        """
        # hook the serial code here
        # if value == 1:
        #    os.system(meta)
        """

    def close(self):
        self.ser.close()

    def syn(self):
        self.ser.flush()

