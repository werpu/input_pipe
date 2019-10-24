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
from ev_core.sourcedevices2 import SourceDevices2
from ev_core.targetdevices import TargetDevices
from ev_core.config import Config
from utils.langutils import save_fetch, build_tree

EV_TYPE = "ev_type"

EV_CODE = "ev_code"

EV_NAME = "ev_name"

DRIVER = "driver"

EV_META = "ev_meta"

EV_PERIODICAL = "periodical"

EV_FREQUENCY = "frequency"


class EventTree:

    def __init__(self, config: Config, sourceDevices: SourceDevices2, targetDevices: TargetDevices):
        # format <from>, <ev_type>, <code> <to> <eventobject>*
        # now id an event is issued we translate the event data beginning
        # from the source over the event type into fine grained mappings
        # and then an evdev event object is returned with all the needed data
        # from the mapping to issue an event

        self.tree = {}
        for rule in save_fetch(lambda: config.rules, []):
            rule_from = rule["from"]
            for target_rules in rule["target_rules"]:
                ev_type_code, from_ev_type, from_ev_code, from_ev_name, value0, from_ev_meta = self.parse_ev(target_rules["from_ev"])
                targets = save_fetch(lambda: target_rules["targets"], [])
                self.assert_targets(targets)

                last_node = build_tree(self.tree, rule_from, from_ev_type, from_ev_code)

                for target in targets:
                    target_to = target["to"]
                    periodical = save_fetch(lambda: target["periodical"], 0)
                    frequency = save_fetch(lambda: target["frequency"], 10)
                    ## todo hook sequence in here somehow
                    self.build_target_rule(last_node, rule_from, target, targetDevices, target_to, periodical, frequency)

    def build_target_rule(self, last_node, rule_from, target, targetDevices, target_to, periodical, frequency):
        ev_type_code, to_ev_type, to_ev_code, to_ev_name, value, to_ev_meta = self.parse_ev(target["to_ev"])

        last_node[target_to] = save_fetch(lambda: last_node[target_to], {
            EV_TYPE: to_ev_type,
            EV_CODE: to_ev_code,
            EV_NAME: to_ev_name,
            EV_META: to_ev_meta,
            EV_PERIODICAL: periodical,
            EV_FREQUENCY: frequency,

            DRIVER: save_fetch(lambda: targetDevices.drivers[target_to])
        })

        if save_fetch(lambda: last_node[target_to][DRIVER]) is None:
            print("Device "+target_to+" not found")
            raise
        if value is not None:
            last_node[target_to]["value"] = value

    @staticmethod
    def parse_ev(evstr):
        splitted = [my_str.strip() for my_str in evstr.split(",")]
        ev_type_code = None
        ev_meta = None

        if splitted[0].find("code") is not -1:
            ev_code, ev_name, ev_type_code, ev_type_full = EventTree._parse_code_def(splitted)
        elif splitted[0].find("META") is not -1:
            ev_code, ev_meta, ev_name, ev_type_full = EventTree._parse_meta(splitted)
        else:
            ev_code, ev_name, ev_type_full = EventTree._parse_normal_def(splitted)

        value = EventTree._parse_value(splitted)

        return ev_type_code, ev_type_full, ev_code, ev_name, value, ev_meta

    @staticmethod
    def _parse_value(splitted):
        value = None
        if len(splitted) > 2:  # value definition exists
            value_def = splitted[2]
            if value_def.find("value") is not -1:
                value = value_def.split()[1].strip()
        return value

    @staticmethod
    def _parse_normal_def(splitted):
        ev_type_full = splitted[0][1:-1].strip()
        ev_code, ev_name = EventTree._parse_event_codes(splitted)
        return ev_code, ev_name, ev_type_full

    @staticmethod
    def _parse_meta(splitted):
        ev_type_full = splitted[0][1:-1].strip()
        ev_code = None
        ev_name = None
        ev_meta = splitted[1].strip()
        return ev_code, ev_meta, ev_name, ev_type_full

    @staticmethod
    def _parse_code_def(splitted):
        type_codes = [my_str.strip() for my_str in splitted[0].split()]
        ev_type_code = type_codes[1]
        ev_type_full = type_codes[2][1:-1].strip()
        ev_code, ev_name = EventTree._parse_event_codes(splitted)
        return ev_code, ev_name, ev_type_code, ev_type_full

    @staticmethod
    def _parse_event_codes(splitted):
        evcodes = [my_str.strip() for my_str in splitted[1].split()]
        ev_code = evcodes[1].strip()
        ev_name = evcodes[2][1:-1].strip()
        return ev_code, ev_name

    @staticmethod
    def assert_targets(targets):
        if len(targets) == 0:
            raise ValueError("No targets in rule defined")



