import unittest

class TestCase_from_string(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import logging
        from pyee.units.types import Prefix
        cls.Prefix = Prefix

    def test_from_string_simple(self):
        p = self.Prefix("k")
        self.assertEqual(p.f, 1000)
        p = self.Prefix.from_name("kilo")
        self.assertEqual(p.f, 1000)

        p = self.Prefix.from_number(0.000015)
        self.assertEqual(p.s, "u")

        p = self.Prefix.from_number(0.0015)
        self.assertEqual(p.s, "m")

        p = self.Prefix.from_number(0.15)
        self.assertEqual(p.s, "m")

        p = self.Prefix.from_number(15)
        self.assertEqual(p.s, "")

        p = self.Prefix.from_number(134.3)
        self.assertEqual(p.s, "")

        p = self.Prefix.from_number(1215.2)
        self.assertEqual(p.s, "k")

class TestCase_from_number(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pyee.units.types import Prefix
        cls.Prefix = Prefix


if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.units.types import logger
    logger.setLevel(logging.INFO)

    unittest.main()
