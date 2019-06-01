
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



