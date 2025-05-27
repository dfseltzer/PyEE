import unittest

class TestCase_create(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import logging
        from pyee.types.physicalquantity import PhysicalQuantity
        cls.PQ = PhysicalQuantity

    def test_create(self):
        p1 = self.PQ.from_value(50000,"kg")
        self.assertEqual(p1.p.s,"k")
        self.assertEqual(p1.v, 50)
        self.assertEqual(p1.u, "kg")

        p2 = self.PQ.from_value(0.1, "m/s^2")
        self.assertEqual(p2.p.s,"m")
        self.assertEqual(p2.v, 100)
        self.assertEqual(p2.u, "m/s^2")

    def test_from_string(self):
        p1 = self.PQ.from_string("0.0001")
        p2 = self.PQ.from_string("0.1m")
        p3 = self.PQ.from_string("0.1 H")
        p4 = self.PQ.from_string("0.1m H")
        
        self.assertAlmostEqual(p1.v, 100)
        self.assertEqual(p1.p, "u")
        self.assertEqual(p1.u, "1")

        self.assertAlmostEqual(p2.v, 100)
        self.assertEqual(p2.p, "u")
        self.assertEqual(p2.u, "1")

        self.assertAlmostEqual(p3.v, 100)
        self.assertEqual(p3.p, "m")
        self.assertEqual(p3.u, "H")

        self.assertAlmostEqual(p4.v, 100)
        self.assertEqual(p4.p, "u")
        self.assertEqual(p4.u, "H")

    def test_multiply_instance(self):
        p1 = self.PQ.from_value(50000, "kg")
        p2 = self.PQ.from_value(0.1, "m/s^2")
        p3 = p1*p2
        self.assertEqual(p3.p.s,"k")
        self.assertEqual(p3.v, 5)
        self.assertEqual(p3.u, "kg.m/s^2")

    def test_multiply_scalar(self):
        p1 = self.PQ.from_value(50000, "kg")
        p2 = self.PQ.from_value(0.1, "m/s^2")
        p3 = p1 * p2
        p4 = p3 * 300
        self.assertEqual(p4.p.s, "M")
        self.assertEqual(p4.v, 1.5)
        self.assertEqual(p4.u, "kg.m/s^2")

    def test_subtract(self):
        p1 = self.PQ.from_value(60.125, "kg")
        p2 = self.PQ.from_value(20.5, "m")
        p3 = self.PQ.from_value(400, "kg")

        p4 = p1-p3
        self.assertEqual(p4.p.s, "")
        self.assertEqual(p4.v, 60.125-400)
        self.assertEqual(p4.u, "kg")

        self.assertRaises(TypeError, lambda: p1-p2)

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
