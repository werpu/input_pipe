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

import unittest
from ev_core.config import Config
from utils.langutils import *


class MyTestCase(unittest.TestCase):

    def test_basic_config(self):
        conf = Config("../resources/devices.yaml")
        self._assert_basic_structure(conf)

    def test_basic_template(self):
        conf = Config("../resources/devices.json5.vtpl")
        self._assert_basic_structure(conf)
        
    def test_overlay(self):
        conf = Config("../resources/devices.yaml")
        conf.overlay("../resources/overlay.yaml")
        self._assert_overlayed_structure(conf)

    def test_basic_config_json5(self):
        conf = Config("../resources/devices.json5")
        self._assert_basic_structure(conf)

    def test_overlay_json5(self):
        conf = Config("../resources/devices.json5")
        conf.overlay("../resources/overlay.yaml")
        self._assert_overlayed_structure(conf)

    def test_basic_config_toml(self):
        conf = Config("../resources/devices.toml")
        self._assert_basic_structure(conf)

    def test_overlay_toml(self):
        conf = Config("../resources/devices.toml")
        conf.overlay("../resources/overlay.yaml")
        self._assert_overlayed_structure(conf)

    def _assert_basic_structure(self, conf):
        self.assertNotEqual(save_fetch(lambda: conf.inputs["digital"]["name"], None), None, "structure exists")
        self.assertNotEqual(conf.rules[0]["from"], None, "structure exists")

    def _assert_overlayed_structure(self, conf):
        self.assertEqual(save_fetch(lambda: conf.rules[1]["from"], None), "analog_left")
        self.assertEqual(save_fetch(lambda: conf.rules[1]["target_rules"][1]["targets"][0]["to_ev"],
                                    None), "(META), overlayed")
        self.assertEqual(save_fetch(lambda: conf.rules[1]["target_rules"][1]["targets"][0]["to"],
                                    None), "booga1")
        self.assertEqual(save_fetch(lambda: conf.rules[2]["target_rules"][1]["targets"][0]["to"],
                                    None), "exec1")
        self.assertEqual(save_fetch(lambda: conf.rules[1]["target_rules"][2]["targets"][0]["to"],
                                    None), "bongobongo")
        conf.reset_config()
        self.assertEqual(save_fetch(lambda: conf.rules[2]["target_rules"][0]["targets"][0]["to_ev"],
                                    None), "(META), /usr/local/bin/4way")
        self.assertEqual(save_fetch(lambda: conf.rules[2]["target_rules"][1]["targets"][0]["to"],
                                    None), "exec1")


if __name__ == '__main__':
    unittest.main()
