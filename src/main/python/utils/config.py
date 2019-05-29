import yaml
import io
import json

class Config:

    def __init__(self, configfile='devices.yaml'):

        stream = open(configfile, 'r')
        self.__dict__ = yaml.load(stream, Loader=yaml.FullLoader)
        stream.close()


INPUTS = "inputs"
PHYS_RE = "phys_re"
NAME_RE = "name_re"
PHYS = "phys"
NAME = "name"
RELPOS = "relpos"