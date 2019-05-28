#!/usr/bin/python3

import re

class r(str):
    def m(self, q):
        return re.findall(q, self)
    def mf(self, q):
        if not re.search(q, self) is None:
            return r(re.findall(q, self)[0])
        else:
            return False
    def c(self, q):
        return not re.search(q, self) is None
    def r(self, q, rep):
        return r(re.sub(q, rep, self))
    def rf(self, q, rep):
        return r(re.sub(q, rep, self, 1))
    def d(self, q):
        return r(re.sub(q, '', self))
    def l(self, q):
        return len(re.findall(q, self))
    def split(self, q):
        return re.split(q, self)

