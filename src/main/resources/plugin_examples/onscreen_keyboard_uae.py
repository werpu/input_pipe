# Keyboard starter for the florence keyboard
# utilizing the uaw shortcuts of middle mouse to release the mouse pointer
# and right mouse to capture it again
# you can use this script for your own toggle functionalities
# ideally you probably shuld use overlays to customly attach your own
# generic on screen keyboard to an emulator, since every emulator has
# different shortcuts
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
            self.mouse_driver.press_btn_middle()
            self.start_florence()
        else:
            self.mouse_driver.press_btn_right()
            self.kill_florence()


drv = globals()["drivers"]
OSKeyHandler(drv["mouse1"]).toggle_florence()

