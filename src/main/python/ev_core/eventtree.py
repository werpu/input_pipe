# MIT License
#
# Copyright (c) 2019 Werner Punz
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# the event tree the base data structure for our event pipe
from ev_core.sourcedevices import SourceDevices
from ev_core.targetdevices import TargetDevices
from ev_core.config import Config
from utils.langutils import save_fetch, build_tree

EV_TYPE = "ev_type"

EV_CODE = "ev_code"

EV_NAME = "ev_name"

DRIVER = "driver"


class EventTree:

    def __init__(self, config: Config, sourceDevices: SourceDevices, targetDevices: TargetDevices):
        # format <from>, <ev_type>, <code> <to> <eventobject>*
        # now id an event is issued we translate the event data beginning
        # from the source over the event type into fine grained mappings
        # and then an evdev event object is returned with all the needed data
        # from the mapping to issue an event

        self.tree = {}
        for rule in save_fetch(lambda: config.rules, []):
            rule_from = rule["from"]
            for target_rules in rule["target_rules"]:
                ev_type_code, from_ev_type, from_ev_code, from_ev_name, value0 = self.parse_ev(target_rules["from_ev"])
                targets = save_fetch(lambda: target_rules["targets"], [])
                self.assert_targets(targets)

                last_node = build_tree(self.tree, rule_from, from_ev_type, from_ev_code)

                for target in targets:
                    target_to = target["to"]
                    self.build_target_rule(last_node, rule_from, target, targetDevices, target_to)

    def build_target_rule(self, last_node, rule_from, target, targetDevices, target_to):
        ev_type_code, to_ev_type, to_ev_code, to_ev_name, value = self.parse_ev(target["to_ev"])

        last_node[target_to] = save_fetch(lambda: last_node[target_to], {
            EV_TYPE: to_ev_type,
            EV_CODE: to_ev_code,
            EV_NAME: to_ev_name,
            DRIVER: save_fetch(lambda: targetDevices.drivers[target_to])
        })

        if save_fetch(lambda: last_node[target_to][DRIVER]) is None:
            print("Device "+target_to+" not found")
            raise
        if value is not None:
            last_node[target_to]["value"] = value


    def parse_ev(self, evstr):
        splitted = [my_str.strip() for my_str in evstr.split(",")]
        ev_type_code = None
        if splitted[0].find("code") is not -1:
            type_codes = [my_str.strip() for my_str in splitted[0].split()]
            ev_type_code = type_codes[1]
            evtype_full = type_codes[2][1:-1].strip()
        else:
            evtype_full = splitted[0][1:-1].strip()
        evcodes = [my_str.strip() for my_str in splitted[1].split()]
        evcode = evcodes[1].strip()
        evname = evcodes[2][1:-1].strip()

        value = None
        if len(splitted) > 2: #value definition exists
            value_def = splitted[2]
            if value_def.find("value") is not -1:
                value = value_def.split()[1].strip()

        return ev_type_code, evtype_full, evcode, evname, value

    @staticmethod
    def assert_targets(targets):
        if len(targets) == 0:
            raise ValueError("No targets in rule defined")



