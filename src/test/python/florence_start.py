import os
import time
import psutil


class OSKeyHandler:

    def __init__(self, mouse1):
        self.mouse_driver = mouse1

    def kill_florence(self):
        p = self.florence_exists()
        if p is not None:
            p.terminate()
            time.sleep(0.5)
            self.mouse_driver.press_btn_left()

    @staticmethod
    def florence_exists():
        p = None
        for proc in psutil.process_iter():
            if proc.as_dict(attrs=["name"])["name"] == "florence":
                p = proc
                break
        return p

    def start_florence(self):
        if self.florence_exists() is None:
            os.system("florence &")

    def toggle_florence(self):
        if self.florence_exists() is None:
            self.start_florence()
            self.mouse_driver.press_btn_middle()
        else:
            self.kill_florence()


#cfg = globals()["config"]
#drv = globals()["drivers"]
# middle mouse (EV_KEY), code 274 (BTN_MIDDLE)
# florence /usr/bin/florence
# btn-left: (EV_KEY), code 272 (BTN_LEFT)


drv = globals()["drivers"]
OSKeyHandler(drv["mouse1"]).toggle_florence()


