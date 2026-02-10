import unittest

class TestCase_create_numeric(unittest.TestCase):
    """Test PassiveComponent instantiation with numeric values using singledispatch"""
    @classmethod
    def setUpClass(cls):

        from pyee.passives import Inductor, Capacitor, Resistor
        cls.Inductor = Inductor
        cls.Capacitor = Capacitor
        cls.Resistor = Resistor

    def test_inductor_numeric(self):
        """Test creating Inductor with numeric value (0.001)"""
        L1 = self.Inductor(0.001)

        self.assertEqual(L1.v, 1.0)
        self.assertEqual(L1.p.s, "m")

    def test_resistor_numeric(self):
        """Test creating Resistor with numeric value (1000)"""
        R1 = self.Resistor(1000)

        self.assertEqual(R1.v, 1.0)
        self.assertEqual(R1.p.s, "k")

    def test_capacitor_numeric(self):
        """Test creating Capacitor with numeric value (0.000001)"""
        C1 = self.Capacitor(0.000001)

        self.assertEqual(C1.v, 1.0)
        self.assertEqual(C1.p.s, "u")

    def test_inductor_numeric_no_prefix(self):
        """Test creating Inductor with numeric value (1)"""
        L1 = self.Inductor(1)

        self.assertEqual(L1.v, 1.0)
        self.assertEqual(L1.p.s, "")

    def test_resistor_numeric_no_prefix(self):
        """Test creating Resistor with numeric value (1)"""
        R1 = self.Resistor(1)

        self.assertEqual(R1.v, 1.0)
        self.assertEqual(R1.p.s, "")


class TestCase_create_string(unittest.TestCase):
    """Test PassiveComponent instantiation with string values using singledispatch"""
    @classmethod
    def setUpClass(cls):

        from pyee.passives import Inductor, Capacitor, Resistor
        cls.Inductor = Inductor
        cls.Capacitor = Capacitor
        cls.Resistor = Resistor

    def test_inductor_string_no_units(self):
        """Test creating Inductor from string with value and prefix only"""
        L1 = self.Inductor("1m")

        self.assertEqual(L1.v, 1.0)
        self.assertEqual(L1.p.s, "m")

    def test_inductor_string_with_units(self):
        """Test creating Inductor from string with value, prefix and units"""
        L2 = self.Inductor("1m H")

        self.assertEqual(L2.v, 1.0)
        self.assertEqual(L2.p.s, "m")

    def test_resistor_string_no_units(self):
        """Test creating Resistor from string with value and prefix only"""
        R1 = self.Resistor("1k")

        self.assertEqual(R1.v, 1.0)
        self.assertEqual(R1.p.s, "k")

    def test_resistor_string_with_units(self):
        """Test creating Resistor from string with value, prefix and units"""
        R2 = self.Resistor("1k Ohm")

        self.assertEqual(R2.v, 1.0)
        self.assertEqual(R2.p.s, "k")

    def test_capacitor_string_no_units(self):
        """Test creating Capacitor from string with value and prefix only"""
        C1 = self.Capacitor("1u")

        self.assertEqual(C1.v, 1.0)
        self.assertEqual(C1.p.s, "u")

    def test_capacitor_string_with_units(self):
        """Test creating Capacitor from string with value, prefix and units"""
        C2 = self.Capacitor("1u F")

        self.assertEqual(C2.v, 1.0)
        self.assertEqual(C2.p.s, "u")

    def test_inductor_string_no_prefix(self):
        """Test creating Inductor from string with value only (no prefix)"""
        L1 = self.Inductor("1")

        self.assertEqual(L1.v, 1.0)
        self.assertEqual(L1.p.s, "")

    def test_resistor_string_large_value(self):
        """Test creating Resistor from string with large numeric value"""
        R1 = self.Resistor("47k")

        self.assertEqual(R1.v, 47.0)
        self.assertEqual(R1.p.s, "k")

    def test_capacitor_string_nano(self):
        """Test creating Capacitor from string with nano prefix"""
        C1 = self.Capacitor("100n")

        self.assertEqual(C1.v, 100.0)
        self.assertEqual(C1.p.s, "n")


class TestCase_create_with_prefix_kwarg(unittest.TestCase):
    """Test PassiveComponent instantiation with prefix keyword argument"""
    @classmethod
    def setUpClass(cls):
        from pyee.passives import Inductor, Capacitor, Resistor
        from pyee.types.prefixes import Prefix
        cls.Inductor = Inductor
        cls.Capacitor = Capacitor
        cls.Resistor = Resistor
        cls.Prefix = Prefix

    def test_numeric_with_prefix_kwarg(self):
        """Test creating Inductor with numeric value and prefix kwarg"""
        p = self.Prefix.from_string("m")
        L1 = self.Inductor(1, prefix=p)

        self.assertEqual(L1.v, 1.0)
        self.assertEqual(L1.p.s, "m")

    def test_string_with_prefix_kwarg(self):
        """Test creating Resistor with string value and prefix kwarg"""
        p = self.Prefix.from_string("k")
        R1 = self.Resistor("1", prefix=p)

        self.assertEqual(R1.v, 1.0)
        self.assertEqual(R1.p.s, "k")


class TestCase_create_invalid_inputs(unittest.TestCase):
    """Test PassiveComponent instantiation with invalid inputs"""
    @classmethod
    def setUpClass(cls):

        from pyee.passives import Inductor, Capacitor, Resistor
        cls.Inductor = Inductor
        cls.Capacitor = Capacitor
        cls.Resistor = Resistor

    def test_invalid_type_raises_error(self):
        """Test that invalid input type raises ValueError"""
        with self.assertRaises(ValueError):
            self.Inductor([1, 2, 3])

    def test_resistor_wrong_units_raises_error(self):
        """Test that creating Resistor with wrong units raises UnitsMissmatchException"""
        from pyee.exceptions import UnitsMissmatchException
        from pyee.types.units import Units
        
        wrong_units = Units.from_string("H")  # Henry instead of Ohm
        with self.assertRaises(UnitsMissmatchException):
            self.Resistor(1000, units=wrong_units)

    def test_capacitor_wrong_units_raises_error(self):
        """Test that creating Capacitor with wrong units raises UnitsMissmatchException"""
        from pyee.exceptions import UnitsMissmatchException
        from pyee.types.units import Units
        
        wrong_units = Units.from_string("Ohm")  # Ohm instead of Farad
        with self.assertRaises(UnitsMissmatchException):
            self.Capacitor(1e-6, units=wrong_units)


if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
