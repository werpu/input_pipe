# plugin which demonstrates
# how to toggle a state
# on a keypress, for simplicity reasons we just start vlc in hidden mode
import os

cfg = globals()["config"]
drv = globals()["drivers"]

if "a_autofire_press" in cfg:
    del cfg["a_autofire_press"]
    os.system("/home/werpu/gamepadservice/reset.sh")
    pass
else:
    cfg["a_autofire_press"] = True
    os.system("/home/werpu/gamepadservice/a-autofire.sh")
    pass


