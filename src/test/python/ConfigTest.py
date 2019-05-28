import unittest
from utils.config import Config


class MyTestCase(unittest.TestCase):
    def test_something(self):
        conf = Config()
        self.assertNotEqual(conf.inputs["stick1"]["name"], None, "structure exists")
        self.assertNotEqual(conf.rules[0]["from"], None, "structure exists")





if __name__ == '__main__':
    unittest.main()
