import unittest

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class TestCase_create(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from pyee.types.physicalquantity import DependantPhysicalQuantity
        cls.DPQ = DependantPhysicalQuantity

    def test_create(self):
        # just make sure these do not error out
        self.DPQ()
        self.DPQ(num=[1,2,3], den=[4,5,6])
        self.DPQ(den=[4,5,6], var0=2)
        self.DPQ(var0=2, var_units="Hz")
        self.DPQ(num=[1,2,3], den=[4,5,6], var0=2, var_units="Hz")
        
    def test_call_var0(self):
        # no arguments, so calls with default variable
        z1 = self.DPQ(num=[1, 1], den=[1], var_units="kg")
        self.assertRaises(ValueError, lambda: z1())
        z1.var0 = 5
        v1 = z1()
        self.assertEquals(v1, 6)

    def test_call_scalar(self):
        z1 = self.DPQ(num=[1, 1], den=[1], var_units="kg")
        v2 = z1(7)
        self.assertEquals(v2, 8)

    def test_call_array(self):
        z1 = self.DPQ(num=[1, 1], den=[1], var_units="kg")
        v3 = z1([2, 3])
        
        self.assertListEqual(list(v3.value), [3, 4])        

    def test_multiply_instance(self):
        z1 = self.DPQ(num=[1, 1], den=[1], units="kg")
        z2 = self.DPQ(num=[2], den=[1], units="1/s")
        
        z3 = z1*z2

        self.assertEquals(z3(1).value, 4)
        self.assertEquals(z3.u, "kg/s")

    def test_multiply_scalar(self):
        z1 = self.DPQ(num=[1, 1], den=[1], units="kg", var_units="s")
        z2 = z1*5

        self.assertEquals(z2(1).value, 10)
        self.assertEquals(z2.u, "kg")

    def test_subtract(self):
        pass

if __name__ == '__main__':
    import logging
    unittest.main()
