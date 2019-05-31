
# the event tree the base data structure for our event pipe
from utils.config import Config
from utils.langutils import save_fetch


class EventTree:

    def __init__(self, config: Config):
        # format <from>, <ev_type>, <code> <to> <eventobject>*
        # now id an event is issued we translate the event data beginning
        # from the source over the event type into fine grained mappings
        # and then an evdev event object is returned with all the needed data
        # from the mapping to issue an event

        self.tree = {}
        for rule in save_fetch(lambda: config.rules, []):
            rule_from = rule.__getattribute__("from")
            from_ev_type, from_ev_code, from_ev_name = self.parse_ev(rule.__getattribute__("from_ev"))
            targets = save_fetch(lambda: rule.__getattribute__("targets"), [])
            self.assert_targets(targets)

            self.tree[rule_from] = save_fetch(lambda: self.tree[rule_from], {})

            for target in targets:
                target_to = target.__getattribute__("to")
                self.tree[rule_from][target_to] = save_fetch(lambda: self.tree[rule_from][target_to], {})
                to_ev_type, to_ev_code, to_ev_name = self.parse_ev(target.__getattribute__("to_ev"))
                self.tree[rule_from][target_to][to_ev_type] = \
                    save_fetch(lambda: self.tree[rule_from][target_to][to_ev_type], {})
                self.tree[rule_from][target_to][to_ev_type][to_ev_code] = \
                    save_fetch(lambda: self.tree[rule_from][target_to][to_ev_type][to_ev_code], target_to)
                self.tree[rule_from][target_to][to_ev_type][to_ev_name] = \
                    save_fetch(lambda: self.tree[rule_from][target_to][to_ev_type][to_ev_name], target_to)


    def parse_ev(self, evstr):
        splitted = [my_str.strip() for my_str in evstr.split(",")]
        evtype = splitted[0][1:-1].strip()
        evcodes = [my_str.strip() for my_str in splitted[1].split()]
        evcode = evcodes[1].strip()
        evname = evcodes[2][1:-1].strip()

        return evtype, evcode, evname

    def assert_targets(self, targets):
        if len(targets) == 0:
            raise ValueError("No targets in rule defined")



