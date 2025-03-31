import unittest

import numpy

from pyee.math.polynomials import polyeval
from pyee.math.polynomials import polymul

class TestCase_polyeval(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p1 = [1] # 1
        cls.p2 = [0,1,2] # x + 2*x^2
        cls.p3 = [0,0,0.5] # 0.5*x^2

        cls.a1 = numpy.array(cls.p1)
        cls.a2 = numpy.array(cls.p2)
        cls.a3 = numpy.array(cls.p3)

    
    def test_single_points(self):
        self.assertEqual(polyeval(self.p1, 1), 1)
        self.assertEqual(polyeval(self.a1, 1), 1)
        self.assertEqual(polyeval(self.p2, 2), 10)
        self.assertEqual(polyeval(self.a2, 2), 10)
        self.assertEqual(polyeval(self.p3, 3), 4.5)
        self.assertEqual(polyeval(self.a3, 3), 4.5)

    def test_py_types(self):
        pass

    def test_numpy_types(self):
        pass

class TestCase_polymul(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p1 = [1] # 1
        cls.p2 = [0,1,2] # x + 2*x^2
        cls.p3 = [0,0,0.5] # 0.5*x^2

        cls.a1 = numpy.array(cls.p1)
        cls.a2 = numpy.array(cls.p2)
        cls.a3 = numpy.array(cls.p3)

    def test_py_types(self):
        self.assertListEqual(list(polymul(self.p1, self.p2)),[0, 1, 2])
        self.assertListEqual(list(polymul(self.p2, self.p3)),[0, 0, 0, 0.5, 1])
        self.assertListEqual(list(polymul(self.p3, self.p1)),[0, 0, 0.5])

    def test_numpy_types(self):
        self.assertTrue((polymul(self.a1, self.a2)==numpy.array([0, 1, 2])).all())
        self.assertTrue((polymul(self.a2, self.a3)==numpy.array([0, 0, 0, 0.5, 1])).all())
        self.assertTrue((polymul(self.a3, self.a1)==numpy.array([0, 0, 0.5])).all())

if __name__ == '__main__':
    import logging
    logging.getLogger().setLevel(logging.INFO)
    unittest.main()
