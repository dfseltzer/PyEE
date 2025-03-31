import unittest

class TestCase_from_string(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import logging
        from pyee.types.units import Prefix
        cls.Prefix = Prefix

    def test_from_string(self):
        p = self.Prefix("k")
        self.assertEqual(p.f, 1000)
        p = self.Prefix.from_name("kilo")
        self.assertEqual(p.f, 1000)

    def test_from_number(self):
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

    def test_from_number_edges(self):
        p = self.Prefix.from_number(999)
        self.assertEqual(p.s, "")

        p = self.Prefix.from_number(1000)
        self.assertEqual(p.s, "k")

        p = self.Prefix.from_number(1001)
        self.assertEqual(p.s, "k")

class TestCase_from_number(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pyee.types.units import Prefix
        cls.Prefix = Prefix


if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
