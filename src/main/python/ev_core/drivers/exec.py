from ev_core.config import Config
from ev_core.drivers.basedriver import BaseDriver
import os


#
# A simple noń virtual driver
# which allows to trigger external processes
# it uses the meta data to trigger the external
# command delivered by meta
class ExecDriver(BaseDriver):
    _init_cnt = 0

    def __init__(self):
        self.phys = "exec" + ExecDriver._init_cnt.__str__()
        ExecDriver._init_cnt += 1
        pass

    def create(self):
        pass

    def write(self, config: Config, drivers, e_type, e_sub_type, value, meta=None):
        if value == 1:
            os.system(meta)

    def close(self):
        pass

    def syn(self):
        pass
