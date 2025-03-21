import unittest


class TestCase_from_string(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import logging
        from pyee.units.units import Units

        cls.Units = Units

    def test_from_string_simple(self):
        # no denominator
        u = self.Units.from_string("m.s")
        self.assertListEqual(u.s, [("m", 1), ("s", 1)])

        u = self.Units.from_string("m.s^-1")
        self.assertListEqual(u.s, [("m", 1), ("s", -1)])

        u = self.Units.from_string("m^-1.s")
        self.assertListEqual(u.s, [("m", -1), ("s", 1)])

        u = self.Units.from_string("m.s.kg^2")
        self.assertListEqual(u.s, [("m", 1), ("s", 1), ("kg", 2)])

    def test_from_string_no_parens(self):
        # no parentheses in denominator
        u = self.Units.from_string("m/s/kg^2")
        self.assertListEqual(u.s, [("m", 1), ("s", -1), ("kg", -2)])

    def test_from_string_parens(self):
        u = self.Units.from_string("m/(s.kg^2)")
        self.assertListEqual(u.s, [("m", 1), ("s", -1), ("kg", -2)])

        u = self.Units.from_string("m/(s)/(kg^2)")
        self.assertListEqual(u.s, [("m", 1), ("s", -1), ("kg", -2)])

class TestCase_Units_cancels(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import logging
        from pyee.units.units import Units
        cls.Units = Units

    def test_from_string_cancels(self):
        u = self.Units()
        u.s = [("kg", -2), ("m", 1), ("s", 1), ("s", -1)]
        u.cancel()
        self.assertListEqual(sorted(u.s, key=lambda e: e[0]), [("kg", -2), ("m", 1)])

        u.s = [("kg", -2), ("m", 1), ("m", -1), ("s", 1), ("s", -1)]
        u.cancel()
        self.assertListEqual(u.s, [("kg", -2)])

        u.s = [("m", 1), ("m", -1)]
        u.cancel()
        self.assertListEqual(u.s, [])


if __name__ == '__main__':
    import context
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.units.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
