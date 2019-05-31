import unittest

from utils.langutils import *


class MyTestCase(unittest.TestCase):

    def test_elvis(self):
        a = {'a': 3, "b": {"c": 5}}
        self.assertEqual(save_fetch(lambda: a['b']['c'], "booga"), 5)
        self.assertEqual(save_fetch(lambda: a['b']['d'], "booga"), "booga")
        self.assertIsNone(save_fetch(lambda: a['b']['d']))

    def test_caseless_equal(self):
        self.assertTrue(caseless_equal("AAA", "AaA"))
        self.assertFalse(caseless_equal("AAA", "xaA"))

    def test_re_match(self):
        self.assertTrue(re_match("aaaBBBccc", "^a.*C$"))
        self.assertTrue(re_match("aaaBBBccc", "^a.*c$"))
        self.assertTrue(re_match("aaaBBBccc", "a.*c"))
        self.assertFalse(re_match("aaaBBBccx", "a.*c$"))

    def test_build_tree(self):
        root = {}
        last = build_tree(root, "a", "b", "c")
        last["data"] = "booga"
        self.assertEqual(root["a"]["b"]["c"]["data"],"booga")


if __name__ == '__main__':
    unittest.main()
