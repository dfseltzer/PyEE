import unittest

import numpy
import numpy.testing as npt

from pyee.math.polynomials import polyeval
from pyee.math.polynomials import polymul
from pyee.math.polynomials import polyadd
from pyee.math.polynomials import polysub
from pyee.math.polynomials import polyprint

class PolynomialTestBase(unittest.TestCase):
    """Base class with common test data for polynomial tests."""
    @classmethod
    def setUpClass(cls):
        cls.p1 = [1] # 1
        cls.p2 = [0,1,2] # x + 2*x^2
        cls.p3 = [0,0,0.5] # 0.5*x^2

        cls.a1 = numpy.array(cls.p1)
        cls.a2 = numpy.array(cls.p2)
        cls.a3 = numpy.array(cls.p3)

class TestCase_polyeval(PolynomialTestBase):

    def test_single_points_with_lists(self):
        self.assertEqual(polyeval(self.p1, 1), 1)
        self.assertEqual(polyeval(self.p2, 2), 10)
        npt.assert_almost_equal(polyeval(self.p3, 3), 4.5)

    def test_single_points_with_arrays(self):
        self.assertEqual(polyeval(self.a1, 1), 1)
        self.assertEqual(polyeval(self.a2, 2), 10)
        npt.assert_almost_equal(polyeval(self.a3, 3), 4.5)

    def test_array_inputs(self):
        x_values = numpy.array([0, 1, 2, 3])
        result = polyeval(self.p2, x_values)
        expected = numpy.array([0, 3, 10, 21])
        npt.assert_array_equal(result, expected)

    def test_zero_polynomial(self):
        zero_poly = [0]
        self.assertEqual(polyeval(zero_poly, 5), 0)
        npt.assert_array_equal(polyeval(zero_poly, numpy.array([1, 2, 3])), numpy.array([0, 0, 0]))

    def test_empty_array_edge_case(self):
        result = polyeval([], 5)
        npt.assert_array_equal(result, 0)

class TestCase_polymul(PolynomialTestBase):

    def test_multiplication_with_lists(self):
        npt.assert_array_equal(polymul(self.p1, self.p2), [0, 1, 2])
        npt.assert_array_almost_equal(polymul(self.p2, self.p3), [0, 0, 0, 0.5, 1])
        npt.assert_array_almost_equal(polymul(self.p3, self.p1), [0, 0, 0.5])

    def test_multiplication_with_arrays(self):
        npt.assert_array_equal(polymul(self.a1, self.a2), numpy.array([0, 1, 2]))
        npt.assert_array_almost_equal(polymul(self.a2, self.a3), numpy.array([0, 0, 0, 0.5, 1]))
        npt.assert_array_almost_equal(polymul(self.a3, self.a1), numpy.array([0, 0, 0.5]))

    def test_multiplication_with_zero(self):
        zero_poly = [0]
        result1 = polymul(zero_poly, self.p2)
        result2 = polymul(self.p2, zero_poly)
        result3 = polymul(zero_poly, zero_poly)

        npt.assert_array_equal(result1, [0])
        npt.assert_array_equal(result2, [0])
        npt.assert_array_equal(result3, [0])

    def test_multiplication_identity(self):
        result = polymul([1], self.p2)
        npt.assert_array_equal(result, self.p2)

class TestCase_polyadd(PolynomialTestBase):

    def test_addition_with_lists(self):
        p12 = polyadd(self.p1, self.p2)
        p21 = polyadd(self.p2, self.p1)

        npt.assert_array_equal(p12, [1, 1, 2])
        npt.assert_array_equal(p21, [1, 1, 2])

    def test_addition_with_arrays(self):
        a12 = polyadd(self.a1, self.a2)
        a21 = polyadd(self.a2, self.a1)

        npt.assert_array_equal(a12, numpy.array([1, 1, 2]))
        npt.assert_array_equal(a21, numpy.array([1, 1, 2]))

    def test_addition_with_zero(self):
        zero_poly = [0]
        result = polyadd(zero_poly, self.p2)
        npt.assert_array_equal(result, self.p2)

    def test_addition_commutativity(self):
        result1 = polyadd(self.p2, self.p3)
        result2 = polyadd(self.p3, self.p2)
        npt.assert_array_almost_equal(result1, result2)

class TestCase_polysub(PolynomialTestBase):

    def test_subtraction_with_lists(self):
        p21 = polysub(self.p2, self.p1)
        p32 = polysub(self.p3, self.p2)

        npt.assert_array_equal(p21, [-1, 1, 2])
        npt.assert_array_almost_equal(p32, [0, -1, -1.5])

    def test_subtraction_with_arrays(self):
        a21 = polysub(self.a2, self.a1)
        a32 = polysub(self.a3, self.a2)

        npt.assert_array_equal(a21, numpy.array([-1, 1, 2]))
        npt.assert_array_almost_equal(a32, numpy.array([0, -1, -1.5]))

    def test_subtraction_with_zero(self):
        zero_poly = [0]
        result = polysub(self.p2, zero_poly)
        npt.assert_array_equal(result, self.p2)

    def test_subtraction_self(self):
        result = polysub(self.p2, self.p2)
        npt.assert_array_equal(result, [0, 0, 0])

class TestCase_polyprint(unittest.TestCase):
    def test_constant(self):
        result = polyprint([5])
        self.assertEqual(result, "5.00")

    def test_linear(self):
        result = polyprint([1, 2])
        self.assertEqual(result, "1.00 + 2.00x")

    def test_quadratic(self):
        result = polyprint([0, 1, 2])
        self.assertEqual(result, "1.00x + 2.00x^2")

    def test_with_floats(self):
        # 0.5 is less than float_range minimum of 1, so it uses scientific notation
        result = polyprint([0, 0, 0.5])
        self.assertEqual(result, "5.00E-01x^2")

    def test_with_floats_custom_range(self):
        # With custom float_range, 0.5 should display as decimal
        result = polyprint([0, 0, 0.5], float_range=(0.1, 100))
        self.assertEqual(result, "0.50x^2")

    def test_negative_coefficients(self):
        result = polyprint([1, -2, 3])
        self.assertEqual(result, "1.00 - 2.00x + 3.00x^2")

    def test_custom_variable(self):
        result = polyprint([1, 2], var="y")
        self.assertEqual(result, "1.00 + 2.00y")

    def test_scientific_notation(self):
        result = polyprint([1000, 0.001])
        self.assertEqual(result, "1.00E+03 + 1.00E-03x")

    def test_print_zeros(self):
        result = polyprint([1, 0, 2], print_zeros=True)
        self.assertEqual(result, "1.00 + 0.0x + 2.00x^2")

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()
