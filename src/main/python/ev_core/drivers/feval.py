from ev_core.drivers.basedriver import BaseDriver
import os
import hashlib
from utils.langutils import *

#
# A simple noń virtual driver
# which allows to trigger another python script
# this can be used for macros or whatever comes your mind
#
class FEvalDriver(BaseDriver):
    _init_cnt = 0


    def __init__(self):
        self.phys = "exec" + FEvalDriver._init_cnt.__str__()
        FEvalDriver._init_cnt += 1
        self._file_data = {}
        pass

    def create(self):
        pass

    def write(self, e_type, e_sub_type, value, meta=None):
        key = hashlib.md5(meta).hexdigest()
        if save_fetch(lambda: self._file_data[meta]) is None:
            file = open(meta, "r")
            self._file_data[key] = file.read()
            file.close()

        exec(self._file_data[key])

    def close(self):
        pass
