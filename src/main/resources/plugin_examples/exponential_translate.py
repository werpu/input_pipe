# logarithmic/exponential value translation for delayed sensitivity
# and also example on how to translate event values simply
# with out eval trigger
import math

from evdev import UInput, ecodes

event = globals()["event"]


# euler exponential base for now
def calc(xVal):
    if xVal >= 127:
        return math.exp(xVal * 0.0381) + 127
    else:
        xVal = max(0.001, xVal)
        return math.log(xVal) / 0.0381 - 127


event.value = calc(event.value)






