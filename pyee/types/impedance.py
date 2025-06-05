"""
Extends the Dependant Physical Quantity to behave like an impedance.
"""


import logging

logger = logging.getLogger(__name__)

import numpy as np

from pyee.types.physicalquantity import DependantPhysicalQuantity

from pyee import GLOBAL_TOLERANCE
from pyee.exceptions import UnitsMissmatchException

class Impedance(DependantPhysicalQuantity):
    """
    Represents an impedance as a numerator and denominator polynomial in 's'
    """

    def __init__(self, num, den, frequency=1000, frequency_units="Hz", tol=GLOBAL_TOLERANCE, *args, **kwargs):
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
                         var_units=frequency_units,
                         var_symbol="s",
                         tol=tol)
        
    def simplify(self, **kwargs):
        #TODO add argument to allow "almost equals"

        # remove anything smaller than tolerance
        self.num = np.where(abs(self.num) <= self.tol, 0, self.num)
        self.den = np.where(abs(self.den) <= self.tol, 0, self.den)

        # remove common zero roots if they exist
        numzeros = np.argmin(self.num <= self.tol)
        denzeros = np.argmin(self.den <= self.tol)
        commonzeros = min(numzeros, denzeros) # type: ignore

        if commonzeros:
            logger.info(f"Pass 0: Found [{commonzeros}] common zero root(s), removing.")
            self.num = self.num[commonzeros:]
            self.den = self.den[commonzeros:]
        
        # get front constant, will be lost when converted to roots.
        Kn = self.num[-1] if abs(self.num[-1]) >= self.tol else 1 # Check vs. tol again ... maybe dont need to?
        Kd = self.den[-1] if abs(self.den[-1]) >= self.tol else 1
        self.num = self.num/Kn
        self.den = self.den/Kd
        K = Kn/Kd        

        # switch to roots and remove duplicates
        nz = np.polynomial.polynomial.polyroots(self.num)
        dz = np.polynomial.polynomial.polyroots(self.den)

        simpset = 0
        common = set(nz) & set(dz)            
        ncommon = len(common) > 0
        while ncommon and simpset < 20:  # loop for common roots.
            simpset += 1
            logger.info(f"Pass {simpset}: Removing common roots: {list(float(c) for c in common)}")
            for r in common:
                nz_idx = np.argwhere(nz==r)
                nz = np.delete(nz, nz_idx[0])

                dz_idx = np.argwhere(dz==r)
                dz = np.delete(dz, dz_idx[0])
            common = set(nz) & set(dz)
            ncommon = len(common) > 0

        # put it back together again and re-set num/den values
        self.num = K*np.polynomial.polynomial.polyfromroots(nz)
        self.den = np.polynomial.polynomial.polyfromroots(dz)

        return self

    def __add__(self, value):
        try:
            return super().__add__(value)
        except UnitsMissmatchException as e:
            logger.info(f"Ignoring units missmatch - trying to convert ({value}) to impedances.")
        # convert to Z, and return
        otherZ = value.Z
        return self + otherZ
    
    def __radd__(self, value):
        try:
            return super().__radd__(value)
        except UnitsMissmatchException as e:
            logger.info(f"Ignoring units missmatch - trying to convert ({value}) to impedances.")
        # convert to Z, and return
        otherZ = value.Z
        return otherZ + self 

    def __sub__(self, value):
        try:
            return super().__sub__(value)
        except UnitsMissmatchException as e:
            logger.info(f"Ignoring units missmatch - trying to convert ({value}) to impedances.")
        # convert to Z, and return
        otherZ = value.Z
        print(otherZ)
        return self - otherZ
    
    def __rsub__(self, value):
        try:
            return super().__rsub__(value)
        except UnitsMissmatchException as e:
            logger.info(f"Ignoring units missmatch - trying to convert ({value}) to impedances.")
        # convert to Z, and return
        otherZ = value.Z
        return otherZ - self 