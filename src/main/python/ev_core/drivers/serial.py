import sys
from ev_core.config import Config
from ev_core.drivers.basedriver import BaseDriver
import serial

SYN = 254

START_BYTE = 127

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
            self.ser = serial.Serial(meta, 57600, timeout=0, write_timeout=0)

        except RuntimeError:
            print("Error: ", sys.exc_info()[0])

    def write(self, config: Config, drivers, e_type, e_sub_type, value, meta=None, periodical=0, frequency=0, event=None):
        """
        message format
        [two startbytes of 127 value,
        type byte big endian (high low) unsigned,
        boolean byte marking a negative value,
        two byte value big endian unsigned]
        """
        is_negative = int(value < 0)
        abs_value = abs(value)
        val_high_byte = abs_value >> 8 & 0xff
        value_low_byte = abs_value & 0xff

        s_type = abs(int(e_sub_type))
        type_high_byte = s_type >> 8 & 0xff
        type_low_byte = s_type & 0xff

        # we now transmit the data as byte array
        ev_list = [START_BYTE, START_BYTE, e_type, type_high_byte, type_low_byte, is_negative, val_high_byte, value_low_byte]
        data = bytearray(ev_list)
        self.ser.write(data)
        #
        # Example:
        #    (EV_ABS), code 17 (ABS_HAT0Y), value -1
        #    e_type: EV_ABS - actual 3
        #    e_sub_type: 17
        #    value: 0/1 - value -1
        #

    def close(self):
        """
        close connection
        :return:
        """
        self.ser.close()
        pass

    def syn(self):
        ev_list = [START_BYTE, START_BYTE, 0, 0, SYN, 0, 0, 0]
        data = bytearray(ev_list)
        self.ser.write(data)

        pass
