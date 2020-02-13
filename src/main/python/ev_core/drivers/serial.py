import sys
from ev_core.config import Config
from ev_core.drivers.basedriver import BaseDriver
import serial

TARGET_JOY = 0x0
TARGET_KEYBD = 0x1
TARGET_MOUSE = 0x2

class SerialDriver(BaseDriver):
    """
    Serial driver, for a UART connextion
    to an external board providing
    the joystick emulation to external devices
    """
    _init_cnt = 0

    def __init__(self):
        self.phys = "serial" + SerialDriver._init_cnt.__str__()
        SerialDriver._init_cnt += 1
        self.name = "serial"
        self.ser = None

    def create(self, meta="/dev/serial0"):
        try:
            self.ser = serial.Serial(meta, 9600)
        except RuntimeError:
            print("Error: ", sys.exc_info()[0])

    def write(self, config: Config, drivers, e_type, e_sub_type, value, meta=None, periodical=0, frequency=0, event=None):
        """
        # hook the serial code here
        # if value == 1:
        #    os.system(meta)
        # todo add marker bytes here for stream reovery on the client side
        # a double byte combinatin of ffxff should do the trick
        """
        ev_list = [127, 127, e_type, int(e_sub_type), value < 0, 0, abs(value)]
        data = bytearray(ev_list)
        num_bytes = self.ser.write(data)
        self.ser.flush()
        print(num_bytes)
        """
        Example:
            (EV_ABS), code 17 (ABS_HAT0Y), value -1
            e_type: EV_ABS - actual 3
            e_sub_type: 17
            value: 0/1 - value -1    
        """

    def close(self):
        """
        close connection
        :return:
        """
        self.ser.close()
        pass

    def syn(self):
        """
        flush... identical to joystick syn
        :return:
        """
        self.ser.flush()
        pass
