import unittest

class TestCase_create(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import logging
        from pyee.passives import Inductor, Capacitor, Resistor
        cls.Inductor = Inductor
        cls.Capacitor = Capacitor
        cls.Resistor = Resistor

    def test_create(self):
        L1 = self.Inductor(0.001)

        self.assertEqual(L1.v, 1.0)
        self.assertEqual(L1.p.s, "m")

        #TODO make the following work?
        #L2 = self.Inductor("1m")
        #L3 = self.Inductor("1mH")
        #L4 = self.Inductor("1 m")
        #L5 = self.Inductor("1 mH")
        #L6 = self.Inductor("1 m H")



if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
