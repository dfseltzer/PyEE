import unittest
from pyee.types.physicalquantity import PhysicalQuantity
from pyee.types.prefixes import Prefix
        
class TestCase_create(unittest.TestCase):
    def test_from_value(self):
        p1 = PhysicalQuantity(50000, units="kg")
        self.assertEqual(p1.p.s,"k")
        self.assertEqual(p1.v, 50)
        self.assertEqual(p1.u, "kg")

        p2 = PhysicalQuantity(0.1, units="m/s^2")
        self.assertEqual(p2.p.s,"m")
        self.assertEqual(p2.v, 100)
        self.assertEqual(p2.u, "m/s^2")

    def test_from_string(self):
        p1 = PhysicalQuantity("0.0001")
        p2 = PhysicalQuantity("0.1m")
        p3 = PhysicalQuantity("0.1 H")
        p4 = PhysicalQuantity("0.1m H")
        
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

    def test_from_pq_is_copy(self):
        """Test that creating from a PQ creates a copy."""
        p1 = PhysicalQuantity(100, units="V")
        p2 = PhysicalQuantity(p1)

        self.assertIsNot(p1, p2)
        self.assertEqual(p1, p2)

        # Modify copy and check original is unchanged
        p2.value = 200
        self.assertEqual(p1.value, 100)
        self.assertEqual(p2.value, 200)

    def test_from_numeric_with_prefix_kwarg(self):
        """Test creating from a number with a prefix keyword argument."""
        # 1000 with prefix 'm' (milli) should be 1.
        p1 = PhysicalQuantity(1000, prefix=Prefix.from_string("m"), units="V")
        self.assertAlmostEqual(p1.value, 1)
        self.assertEqual(p1.u, "V")

        # 0.01 with prefix 'u' (micro) should be 10n.
        p2 = PhysicalQuantity(0.01, prefix=Prefix.from_string("u"), units="F")
        self.assertAlmostEqual(p2.value, 1e-8) # 10 nF
        self.assertEqual(p2.v, 10)
        self.assertEqual(p2.p, "n")
        self.assertEqual(p2.u, "F")

    def test_from_string_with_kwargs(self):
        """Test creating from a string with override kwargs."""
        # Units kwarg should override units in string
        p1 = PhysicalQuantity("10 V", units="Ohm")
        self.assertEqual(p1.u, "Ohm")

        # Prefix kwarg should combine with prefix in string
        p2 = PhysicalQuantity("10k", prefix=Prefix.from_string("k"), units="Ohm")
        self.assertAlmostEqual(p2.value, 10_000_000) # 10k * k = 10M

class TestCase_math(unittest.TestCase):
    def test_multiply_instance(self):
        p1 = PhysicalQuantity(50000, units="kg")
        p2 = PhysicalQuantity(0.1, units="m/s^2")
        p3 = p1*p2
        self.assertEqual(p3.p.s,"k")
        self.assertEqual(p3.v, 5)
        self.assertEqual(p3.u, "kg.m/s^2")

    def test_multiply_scalar(self):
        p1 = PhysicalQuantity(50000, units="kg")
        p2 = PhysicalQuantity(0.1, units="m/s^2")
        p3 = p1 * p2
        p4 = p3 * 300
        self.assertEqual(p4.p.s, "M")
        self.assertEqual(p4.v, 1.5)
        self.assertEqual(p4.u, "kg.m/s^2")

    def test_subtract_instance(self):
        p1 = PhysicalQuantity(60.125, units="kg")
        p2 = PhysicalQuantity(20.5, units="m")
        p3 = PhysicalQuantity(400, units="kg")

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
