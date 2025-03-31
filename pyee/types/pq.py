"""
Physical Quantity  and derived classes
"""

import numpy as np

import re
import logging

from ..types.units import Units
from ..types.units import Prefix

class PhysicalQuantity(object):
    def __init__(self, value=None, units=None):
        if value is not None:
            self.p = Prefix.from_number(value)
            self.v = value/self.p
        else:
            self.p = Prefix()
            self.v = None


        self.u = Units.from_any(units)

    def __copy__(self):
        obj = type(self)()
        obj.p = self.p.copy()
        obj.v = self.v
        obj.u = self.u.copy()
        return obj

    def __repr__(self):
        return f"{self.v:7.3f}{self.p} [{self.u}]"

    def __mul__(self, other):
        if isinstance(other, PhysicalQuantity):
            return PhysicalQuantity(
                value=self.v*self.p*other.v*other.p,
                units=self.u*other.u
            )
        else: #try scalar multiply
            return type(self)(value=self.v*self.p*other, units=self.u)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        try:
            self.u - other.u
        except AttributeError as e:
            logger.error(f"Unable to find units for subtraction: {self} and {other}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for subtraction: {self.u} and {other.u}")
            raise e

        return type(self)(value=self.v*self.p - other.v*other.p, units=self.u.copy())

    def __rsub__(self, other):
        try:
            other.u - self.u
        except AttributeError as e:
            logger.error(f"Unable to find units for operation: {other} and {self}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for subtraction: {other.u} and {self.u}")
            raise e

        return type(self)(value=other.v * other.p - self.v * self.p, units=self.u.copy())

    def __add__(self, other):
        try:
            self.u + other.u
        except AttributeError as e:
            logger.error(f"Unable to find units for addition: {self} and {other}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for addition: {self.u} and {other.u}")
            raise e

        return type(self)(value=self.v * self.p + other.v * other.p, units=self.u.copy())

    def __radd__(self, other):
        try:
            other.u + self.u
        except AttributeError as e:
            logger.error(f"Unable to find units for addition: {other} and {self}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for addition: {other.u} and {self.u}")
            raise e

        return type(self)(value=other.v * other.p + self.v * self.p, units=self.u.copy())

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __truediv__(self, other):
        nv = self.v*self.p/(other.v*other.p)
        nu = self.u/other.u
        return type(self)(value=nv, units=nu)

    def __rtruediv__(self, other):
        nv = (other.v * other.p) / self.v * self.p
        nu = other.u /self.u
        return type(self)(value=nv, units=nu)

    def __eq__(self, other):
        if self.u != other.u:
            return False
        elif self.v*self.p != other.v*other.p:
            return False
        else:
            return True

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def value(self):
        """
        :return: value as a scalar
        """
        return self.v*self.p

    def as_base(self, **kwargs):
        """
        converts units to base units in given context

        :return: new Physical Quantities instance in base units
        """

        newunits = self.u.as_base(**kwargs)
        return type(self)(value=self.v*self.p, units=newunits)

    def copy(self):
        return self.__copy__()

    def simplify(self, **kwargs):
        newunits = self.u.simplify(**kwargs)
        return type(self)(value=self.v * self.p, units=newunits)

    def update(self, val):
        """
        deals with updating prefixes and such when setting value
        :param val: new value
        :return: None
        """
        self.p = Prefix.from_number(val)
        self.v = val / self.p


class DependantPhysicalQuantity(object):
    """
    Physical quantity with some dependence - impedance for example.

    Expands the PhysicalQuantity class by replacing the value scalar by a
    ratio of polynomials of some variable (represented by "s").  Internally
    stores as a numerator and denominator array where index is used to
    represent exponent,

    v[s] = n[s] = [n0, n1, n2, ...]
           ----   -----------------
           d[s]   [d0, d1, d2, ...]

    Stored as numpy polynomials internally

    A default value (var0) can be provided - this is used to calculate the quantity 
    value if no other points are given.

    When two dependant physical quanitites are acted on by a math operator, the left argument
    default value is retained.

    """
    def __init__(self, num=None, den=None, units=None, var0=None, var_units=""):
        """
        :param num: numerator array
        :param den: denominator array
        :param units: units as string or units class
        :param var0: default variable value - used when accessing value as scalars
        :param var_units: variable units
        """
        super().__init__()
        self.u = Units.from_any(units)

        self.num = np.polynomial.Polynomial(num if num is not None else [1])
        self.den = np.polynomial.Polynomial(den if den is not None else [1])

        if isinstance(var0, PhysicalQuantity):
            self._var0 = var0
        else:
            self._var0 = PhysicalQuantity(value=var0, units=var_units)

    def __repr__(self):
        try:
            v0 = self.var0
        except:
            v0 = "NONE"
        
        return f"[DPQ({v0}):({self.num})/({self.den}):({self.u})]"

    def __mul__(self, other):
        if isinstance(other, DependantPhysicalQuantity):
            return type(self)(num=self.num*other.num, 
                              den=self.den*other.den,
                              units=self.u * other.u,
                              var0=self._var0.v, var_units=self._var0.u.copy())
        else: #try scalar multiply
            return type(self)(num=self.num.copy()*other, den=self.den.copy(),
                              units=self.u.copy(), var0=self._var0.copy())

    def __rmul__(self, other):
        pass

    def __sub__(self, other):
        try:
            self.u - other.u
        except AttributeError as e:
            logger.error(f"Unable to find units for subtraction: {self} and {other}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for subtraction: {self.u} and {other.u}")
            raise e

        pass

    def __rsub__(self, other):
        try:
            other.u - self.u
        except AttributeError as e:
            logger.error(f"Unable to find units for operation: {other} and {self}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for subtraction: {other.u} and {self.u}")
            raise e

        pass

    def __add__(self, other):
        try:
            self.u + other.u
        except AttributeError as e:
            logger.error(f"Unable to find units for addition: {self} and {other}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for addition: {self.u} and {other.u}")
            raise e

        pass

    def __radd__(self, other):
        try:
            other.u + self.u
        except AttributeError as e:
            logger.error(f"Unable to find units for addition: {other} and {self}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for addition: {other.u} and {self.u}")
            raise e

        pass

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __truediv__(self, other):
        pass

    def __rtruediv__(self, other):
        pass

    def __eq__(self, other):
        pass

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def var0(self):
        if self._var0.v is None:
            raise ValueError("No initial value - was this ever set?")
        return self._var0

    @var0.setter
    def var0(self, val):
        self._var0.update(val)

    def __call__(self, var=None):
        #TODO let this be called with physical quantities as input
        #TODO update to support input arrays

        if var is None:
            var = self.var0.value

        vn = self.num(var)
        vd = self.den(var)

        print(f"###################\n{vn}\n{vd}\n##############")

        return vn/vd

class Impedance(object):
    """
    Represents an impedance as a numerator and denominator polynomial in 's'
    """
    #TODO remove this, replace with EE specific wrapper for dependant PQ class
    def __init__(self, value, frequency=None, frequency_units="Hz", *args, **kwargs):
        """
        Value must be supplied as a tuple (num, den), where num and den
        are arrays of coefficients for increasing powers of s, where the array index is the power of s.

        Units are always "V/A"

        :param value: (num=[a0, a1, a2], den=[b0, b1, b2])
        :param frequency: default frequency for evaluation. defaults to 1kHz
        :param frequency_units: defaults to "Hz". other values are "rad/s"
        """
        super().__init__()

        self.u = Units("V/A")

        if frequency_units == "Hz":
            self.frequency_units = frequency_units
            self.frequency = frequency if frequency is not None else 1000
        elif frequency_units == "rad/s":
            self.frequency_units = frequency_units
            self.frequency = 2000*np.pi
        else:
            raise ValueError(f"Unknown frequency_units: {frequency_units}. Known values are 'Hz' or 'rad/s'")

        self.n = value[0]
        self.d = value[1]
