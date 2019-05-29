import unittest

from utils.langutils import *


class MyTestCase(unittest.TestCase):

    def test_elvis(self):
        a = {'a': 3, "b": {"c": 5}}
        self.assertEqual(el_vis(lambda: a['b']['c'], "booga"), 5)
        self.assertEqual(el_vis(lambda: a['b']['d'], "booga"), "booga")

    def test_caseless_equal(self):
        self.assertTrue(caseless_equal("AAA", "AaA"))
        self.assertFalse(caseless_equal("AAA", "xaA"))

    def test_re_match(self):
        self.assertTrue(re_match("aaaBBBccc", "^a.*C$"))
        self.assertTrue(re_match("aaaBBBccc", "^a.*c$"))
        self.assertTrue(re_match("aaaBBBccc", "a.*c"))
        self.assertFalse(re_match("aaaBBBccx", "a.*c$"))

if __name__ == '__main__':
    unittest.main()
