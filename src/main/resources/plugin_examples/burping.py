# plugin which demonstrates
# how to play a media file
# on a keypress, for simplicity reasons we just start vlc in hidden mode
import os

cfg = globals()["config"]
drv = globals()["drivers"]
print(drv)

os.system("vlc --play-and-exit --intf dummy /home/werpu/PycharmProjects/" +
          "input_pipe/src/test/resources/Burping_2_short.ogg")
