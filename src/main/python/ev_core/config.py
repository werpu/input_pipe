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
import json5
import toml
import yaml
from pymitter import EventEmitter

from utils.langutils import *
import copy
import airspeed
from collections import OrderedDict
from io import StringIO
import os


#
# Universal configuration
# basically the internal representation of our yaml file (1:1)
# with some added functionality for overlaying and restoring
# from a defunct overlay
#
class Config:

    inputs = None
    outputs = None
    rules = None

    def __init__(self, configfile='devices.yaml'):

        stream = open(configfile, 'r')

        try:
            self.orig_data = self.load_file(stream, configfile)
            self.overlay_stack = []
            self.__dict__.update(copy.deepcopy(self.orig_data))
        finally:
            stream.close()

        self.plugin_data = dict()
        self.orig_data["plugin_data"] = dict()
        self.event_emitter = EventEmitter()

    #
    # overlays some aspects of the config
    # useful for dynamic reconfiguration
    #
    def overlay(self, configfile):
        stream = open(configfile, 'r')
        try:
            overlaydata = self.load_file(stream, configfile)
            overlay_meta = dict()
            overlay_meta["data"] = overlaydata
            overlay_meta["file"] = configfile
            self.overlay_stack.append(overlay_meta)
            plugin_data = self.plugin_data
            to_merge_rules = self._merge_rules(copy.deepcopy(self.orig_data), overlay_meta)
            self.__dict__.update(to_merge_rules)
            self.plugin_data = plugin_data

        finally:
            stream.close()

    @staticmethod
    def load_file(stream, configfile):
        if configfile.endswith(".yaml"):
            return yaml.load(stream, Loader=yaml.FullLoader)
        elif configfile.endswith(".json5"):
            return json5.load(stream)
        elif configfile.endswith(".toml"):
            return toml.load(stream)
        elif configfile.endswith(".vtpl"):
            return Config.load_template(stream, configfile)
        elif configfile.endswith(".tpl"):
            return Config.load_template(stream, configfile, ".tpl")
        elif configfile.endswith(".vm"):
            return Config.load_template(stream, configfile, ".vm")
        else:
            raise Exception("Filetype not supported, at the momoment only yaml and json5 configurations are supported")

    #
    # Loads a template and then once merged goes into the parsers
    #
    @staticmethod
    def load_template(stream, configfile, ending=".vtpl"):
        if not configfile.endswith(ending):
            raise Exception("Template does not have vtpl ending")

        loader = airspeed.CachingFileLoader(os.path.dirname(os.path.abspath(configfile)))
        tpl = loader.load_template(configfile)
        merged_template = tpl.merge({}, loader)
        orig_file_name = configfile[:-1 * len(ending)]

        tpl_stream = StringIO(merged_template)
        print("Velocity Macro found!")
        print("Merging template to final configuration: ")
        print("------ final configuration begin ------")
        print(tpl_stream.getvalue())
        print("------ final configuration end ------")
        return Config.load_file(tpl_stream, orig_file_name)

    #
    # handling of multiple stacked overlays, pops the last overlay from the stack
    #
    def pop_overlay(self):
        self.__dict__.update(copy.deepcopy(self.orig_data))
        if len(self.overlay_stack) > 0:
            self.overlay_stack.pop(len(self.overlay_stack))
            self._update_rules()

    def _update_rules(self):
        self.__dict__.update(copy.deepcopy(self.orig_data))
        plugin_data = self.plugin_data
        for overlay in self.overlay_stack:
            to_merge_rules = self._merge_rules(copy.deepcopy(self.orig_data), overlay)
            self.__dict__.update(to_merge_rules)
        self.plugin_data = plugin_data

    def remove_overlay(self, filename):
        self.overlay_stack = list(filter(lambda x: x["file"] != filename, self.overlay_stack))
        self._update_rules()

    #
    # resets the overlays back to its original
    #
    def reset_config(self):
        self.__dict__.update(copy.deepcopy(self.orig_data))
        self.overlay_stack = []

    #
    # performs a full match on the supplied parameters
    #
    @staticmethod
    def full_match(device, name, name_re, phys, phys_re, vendor, product):
        matchers = Config.get_match_map(name, name_re, phys, phys_re, product, vendor)

        found = True
        for key in matchers:
            dev_key = key
            # vendor and product need special handling coming from the lib
            if dev_key == VENDOR:
                found = found and caseless_equal(device.__getattribute__(INFO)[1], matchers[key])
            elif dev_key == product:
                found = found and caseless_equal(device.__getattribute__(INFO)[2], matchers[key])
            elif re_match(key, "^.*_re$"):
                dev_key = dev_key[:-3]
                found = found and re_match(device.__getattribute__(dev_key), matchers[key])
            else:
                found = found and caseless_equal(device.__getattribute__(key), matchers[key])

        return found

    @staticmethod
    def get_match_map(name, name_re, phys, phys_re, product, vendor):
        matchers = {}
        # we also could iterate over the arguments but for the sake
        # of the name mangling we do not
        if name is not None:
            matchers[NAME] = name
        if name_re is not None:
            matchers[NAME_RE] = name_re
        if phys is not None:
            matchers[PHYS] = phys
        if phys_re is not None:
            matchers[PHYS_RE] = phys_re
        if vendor is not None:
            matchers[VENDOR] = vendor
        if vendor is not None:
            matchers[PRODUCT] = product
        return matchers

    #
    # triggers if any of the supplied criteria matches
    #
    @staticmethod
    def any_match(device, name, name_re, phys, phys_re, vendor, product):
        found = False

        if caseless_equal(device.name or "", name or DUMMY_DEFAULT):
            found = True
        elif re_match(device.phys or "", phys or DUMMY_DEFAULT):
            found = True
        elif re_match(device.vendor or "", vendor or DUMMY_DEFAULT):
            found = True
        elif re_match(device.product or "", product or DUMMY_DEFAULT):
            found = True
        elif re_match(device.name or "", name_re or DUMMY_DEFAULT):
            found = True
        elif re_match(device.phys or "", phys_re or DUMMY_DEFAULT):
            found = True
        return found

    # fetches all the input params from the vonfig at position inputs.<key>
    def get_config_input_params(self, key):
        rel_pos = save_fetch(lambda: self.inputs[key][RELPOS], 1)
        name = save_fetch(lambda: self.inputs[key][NAME])
        phys = save_fetch(lambda: self.inputs[key][PHYS])
        name_re = save_fetch(lambda: self.inputs[key][NAME_RE])
        phys_re = save_fetch(lambda: self.inputs[key][PHYS_RE])
        vendor = save_fetch(lambda: self.inputs[key][INFO][1])
        product = save_fetch(lambda: self.inputs[key][INFO][2])
        exclusive = save_fetch(lambda: self.inputs[key][EXCLUSIVE])
        i_max = save_fetch(lambda: self.inputs[key][MAX])
        i_min = save_fetch(lambda: self.inputs[key][MIN])
        i_deadzone = save_fetch(lambda: self.inputs[key][DEADZONE])

        return name, name_re, phys, phys_re, rel_pos, vendor, product, exclusive, i_max, i_min, i_deadzone

    #
    # the idea is to build an index which allows fast access on the existing data
    # and then match the index with the incoming data and update
    # the merged data accordingly
    #
    # the algorithm is
    # from + from_ev identical overwrite the targets rules
    # if not then append the new rule as new entry, so a collission is always
    # an overwrite from incoming
    # and a missing entry is an add
    # removal is not possible, for the time being, since this functionality is mostly used
    # for adding new mappings or reroute new mappings, if you want to disable something
    # rerout the entry to a custom noop eval
    #
    @staticmethod
    def _build_rule_idx(orig_rules):
        rule_idx = {}
        for rule in orig_rules["rules"]:
            device_id = rule["from"]
            for target_rule in rule["target_rules"]:
                from_ev = target_rule["from_ev"]
                for target in target_rule["targets"]:
                    to = target["to"]
                    rule_idx[device_id + "___" + from_ev + "___" + to] = target_rule

        return rule_idx

    def _merge_rules(self, target_rules, overlay_data):
        rule_idx = self._build_rule_idx(target_rules)
        for rule in overlay_data["data"]["rules"]:
            device_id = rule["from"]
            for target_rule in rule["target_rules"]:
                from_ev = target_rule["from_ev"]
                rule_idx = self._handle_replace(device_id, from_ev, target_rules, rule_idx, target_rule)

                for target in target_rule["targets"]:
                    to = target["to"]
                    matched_target_rule = save_fetch(lambda: device_id + "___" + from_ev + "___" + to)
                    if matched_target_rule in rule_idx:
                        rule_idx[matched_target_rule]["targets"] = target_rule["targets"]
                    else:  # device must exist
                        rule = next(x for x in target_rules["rules"] if x["from"] == device_id)
                        new_rule_target = OrderedDict()
                        new_rule_target["from_ev"] = from_ev
                        new_rule_target["targets"] = target_rule["targets"]
                        rule["target_rules"].append(new_rule_target)
        return target_rules

    def _handle_replace(self, device_id, from_ev, target_rules, rule_idx, target_rule):
        if "replace" in target_rule and target_rule["replace"] == "all":
            rules = target_rules["rules"]
            final_rule = None

            filtered_rules = [rule for rule in rules if self._filter_rule(rule, device_id, from_ev)]
            final_removal_arr = []
            for filtered_rule in filtered_rules:
                final_removal_arr.extend([filtered_target_rule for filtered_target_rule in filtered_rule["target_rules"] if filtered_target_rule["from_ev"] == from_ev])

            for final_removal_rule in final_removal_arr:
                for filtered_rule in filtered_rules:
                    filtered_rule["target_rules"].remove(final_removal_rule)

            rule_idx = self._build_rule_idx(target_rules)

        return rule_idx

    @staticmethod
    def _filter_rule(rule, device_id, from_ev):
        if rule["from"] == device_id:
            rules_ = rule["target_rules"]
            for target_rule in rules_:
                if target_rule["from_ev"] == from_ev:
                    return True
                else:
                    pass
        else:
            return False


INPUTS = "inputs"
PHYS_RE = "phys_re"
NAME_RE = "name_re"
PHYS = "phys"
NAME = "name"
RELPOS = "relpos"
VENDOR = "vendor"
PRODUCT = "product"
VERSION = "version"
INFO = "info"
EXCLUSIVE = "exclusive"
MAX = "max"
MIN = "min"
DEADZONE = "deadzone"

