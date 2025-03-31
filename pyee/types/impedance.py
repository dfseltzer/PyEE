"""
Extends the Dependant Physical Quantity to behave like an impedance.
"""


import logging

logger = logging.getLogger(__name__)

import numpy as np

from .pq import DependantPhysicalQuantity

class Impedance(DependantPhysicalQuantity):
    """
    Represents an impedance as a numerator and denominator polynomial in 's'
    """

    def __init__(self, num, den, frequency=1000, frequency_units="Hz", *args, **kwargs):
        """
        Num and den are arrays of coefficients for increasing powers of s, where the array index is the power of s.

        Units are always "V/A"

        :param num: [a0, a1, a2]
        :param den: [b0, b1, b2]
        :param frequency: default frequency for evaluation. defaults to 1k(units)
        :param frequency_units: defaults to "Hz". other values are "rad/s"
        """
        if frequency_units == "Hz":
            self.frequency = frequency if frequency is not None else 1000
        elif frequency_units == "rad/s":
            frequency = frequency if frequency is not None else 2000*np.pi
        else:
            raise ValueError(f"Unknown frequency_units: {frequency_units}. Known values are 'Hz' or 'rad/s'")

        super().__init__(num=num, den=den, units="V/A", 
                         var0=frequency, 
                         var_units=frequency_units)
        
    def simplify(self):
        n = np.polynomial.Polynomial(self.num)
        d = np.polynomial.Polynomial(self.den)

        nz = n.roots()
        dz = d.roots()
        
        common = set(nz) & set(dz) # wont work for repeated roots...

        logger.info(f"simplify {self} - removing common roots: {common}")

        for r in common:
            nz
        print(nz)
        print(dz)

        
