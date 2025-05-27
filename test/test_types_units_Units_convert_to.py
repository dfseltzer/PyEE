import unittest
import numpy

class TestCase_Frequency(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pyee.types.units import Units
        cls.Units = Units
        cls.u_Hz = Units.from_string("Hz")
        cls.u_Rad = Units.from_string("Rad")

    def test_same_to_same(self):
        fconv1 = self.u_Hz.convert_to(self.u_Hz)
        fconv2 = self.u_Rad.convert_to(self.u_Rad)

        test_vector = numpy.random.random(10)
        self.assertListEqual(list(test_vector), list(fconv1(test_vector)))
        self.assertListEqual(list(test_vector), list(fconv2(test_vector)))


    def test_Hz_to_Rad(self):
        fconv = self.u_Hz.convert_to(self.u_Rad)
        nv = fconv(1/(2*numpy.pi))
        self.assertAlmostEqual(nv, 1)

    def test_Rad_to_Hz(self):
        fconv = self.u_Rad.convert_to(self.u_Hz)
        nv = fconv((2*numpy.pi))
        self.assertAlmostEqual(nv, 1)

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    from pyee.types.units import logger
    logger.setLevel(logging.INFO)

    unittest.main()
