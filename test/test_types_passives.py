import unittest

class TestCase_create(unittest.TestCase):
    @classmethod
    def setUpClass(cls):

        from pyee.passives import Inductor, Capacitor, Resistor
        cls.Inductor = Inductor
        cls.Capacitor = Capacitor
        cls.Resistor = Resistor

    def test_create_numeric(self):
        L1 = self.Inductor.from_value(0.001)

        self.assertEqual(L1.v, 1.0)
        self.assertEqual(L1.p.s, "m")

    def test_create_string(self):
        L1 = self.Inductor.from_string("1m")
        L2 = self.Inductor.from_string("1m H")

        self.assertEqual(L1.v, 1.0)
        self.assertEqual(L1.p.s, "m")

        self.assertEqual(L2.v, 1.0)
        self.assertEqual(L2.p.s, "m")


if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
