from ev_core.drivers.exec import ExecDriver


class ExecDriverMock(ExecDriver):

    def __init__(self):
        ExecDriver.__init__(self)
        self.meta = ""

    def write(self, e_type, e_sub_type, value, meta=None):
        self.meta = meta