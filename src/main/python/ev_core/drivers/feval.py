from ev_core.config import Config
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
        self.phys = "eval" + FEvalDriver._init_cnt.__str__()
        FEvalDriver._init_cnt += 1
        self._file_data = {}

    def create(self):
        pass

    def write(self, config: Config, drivers, e_type, e_sub_type, value, meta=None):
        if value == 1:
            key = hashlib.md5(meta.encode("utf-8")).hexdigest()
            if save_fetch(lambda: self._file_data[key]) is None:
                file = open(meta, "r")
                self._file_data[key] = compile(file.read(), meta, "exec")
                file.close()

            exec(self._file_data[key],  {
                "config": config,
                "drivers": drivers,
                "meta": meta
            })

    def close(self):
        pass

    def syn(self):
        pass
