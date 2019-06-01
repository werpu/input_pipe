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
            from_ev_type, from_ev_code, from_ev_name = self.parse_ev(rule["from_ev"])
            targets = save_fetch(lambda: rule["targets"], [])
            self.assert_targets(targets)

            last_node = build_tree(self.tree, rule_from, from_ev_type, from_ev_code)

            for target in targets:
                target_to = target["to"]
                self.build_target_rule(last_node, rule_from, target, targetDevices, target_to)

    def build_target_rule(self, last_node, rule_from, target, targetDevices, target_to):
        to_ev_type, to_ev_code, to_ev_name = self.parse_ev(target["to_ev"])

        last_node[target_to] = save_fetch(lambda: last_node[target_to], {
            "ev_type": to_ev_type,
            "ev_code": to_ev_code,
            "ev_name": to_ev_name,
            "driver": targetDevices.drivers[target_to]
        })

    def parse_ev(self, evstr):
        splitted = [my_str.strip() for my_str in evstr.split(",")]
        evtype = splitted[0][1:-1].strip()
        evcodes = [my_str.strip() for my_str in splitted[1].split()]
        evcode = evcodes[1].strip()
        evname = evcodes[2][1:-1].strip()

        return evtype, evcode, evname

    @staticmethod
    def assert_targets(targets):
        if len(targets) == 0:
            raise ValueError("No targets in rule defined")



