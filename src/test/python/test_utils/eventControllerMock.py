

# A mocked event controller to check whether our routines
# into the starting and restarting are touched correctly
from ev_core.config import Config


class EventControllerMock:

    def __init__(self, config: Config):
        self.started = True
        self.restarted_cnt = 0
        self.config = config

    def start(self):
        self.restarted_cnt += 1
        self.started = True

    def stop(self):
        self.started = False

    def reload(self):
        self.stop()
        self.start()

