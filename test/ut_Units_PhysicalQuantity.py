import unittest


class TestCase_create(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import logging
        from pyee.units.types import PhysicalQuantity
        cls.PQ = PhysicalQuantity

    def test_create(self):
        p1 = self.PQ(50000,"kg")
        self.assertEqual(p1.p.s,"k")
        self.assertEqual(p1.v, 50)
        self.assertEqual(p1.u, "kg")

        p2 = self.PQ(0.1, "m/s^2")
        self.assertEqual(p2.p.s,"m")
        self.assertEqual(p2.v, 100)
        self.assertEqual(p2.u, "m/s^2")

    def test_multiply(self):
        p1 = self.PQ(50000, "kg")
        p2 = self.PQ(0.1, "m/s^2")

        p3 = p1*p2

        print(p3)


if __name__ == '__main__':
    import context
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.units.types import logger
    logger.setLevel(logging.INFO)

    unittest.main()
