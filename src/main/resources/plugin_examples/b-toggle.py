# plugin which demonstrates
# how to toggle a state
# on a keypress, for simplicity reasons we just start vlc in hidden mode
import os

cfg = globals()["config"]
drv = globals()["drivers"]

if "a_autofire_press" in cfg:
    del cfg["b_autofire_press"]
    os.system("/home/werpu/gamepadservice/reset.sh")
    pass
else:
    cfg["b_autofire_press"] = True
    os.system("/home/werpu/gamepadservice/b-autofire.sh")
    pass


