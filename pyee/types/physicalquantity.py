"""
Physical Quantity  and derived classes
"""

import numpy as np

import logging
import copy

from abc import abstractmethod

from .units import Units
from .prefixes import Prefix
from .converters import vpu_from_ustring

from .. import GLOBAL_TOLERANCE

from ..math.polynomials import polyeval
from ..math.polynomials import polymul
from ..math.polynomials import polyadd
from ..math.polynomials import polyprint
from ..math.polynomials import polysub

from ..exceptions import UnitsMissmatchException

logger = logging.getLogger(__name__)


class PhysicalQuantity(object):
    __DEBUG = False

    @classmethod
    def from_string(cls, ustring):
        v, p, u = vpu_from_ustring(ustring)
        return cls(value=v*p, units=u)

    def __init__(self, value, units=None):
        super().__init__()

        if self.__DEBUG: logger.error(f"Creating PQ from value={value}, units={units}")

        self.p = Prefix.from_number(value)
        self.v = 1/self.p * value # avoid python calling __rdiv__ on each element for lists

        if self.__DEBUG: logger.error(f".... p={self.p} ({type(self.p)})")
        if self.__DEBUG: logger.error(f".... v={self.v} ({type(self.v)})")

        self.u = Units.from_any(units)

    def __copy__(self):
        return copy.deepcopy(self)

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
        except UnitsMissmatchException as e:
            logger.error(f"Units not compatible for subtraction: {self.u} and {other.u}")
            raise e

        return type(self)(value=self.v*self.p - other.v*other.p, units=self.u.copy())

    def __rsub__(self, other):
        try:
            other.u - self.u
        except AttributeError as e:
            logger.error(f"Unable to find units for operation: {other} and {self}.  Exception was: {e}")
            raise e
        except UnitsMissmatchException as e:
            logger.error(f"Units not compatible for subtraction: {other.u} and {self.u}")
            raise e

        return type(self)(value=other.v * other.p - self.v * self.p, units=self.u.copy())

    def __add__(self, other):
        try:
            self.u + other.u
        except AttributeError as e:
            logger.error(f"Unable to find units for addition: {self} and {other}.  Exception was: {e}")
            raise e
        except UnitsMissmatchException as e:
            logger.error(f"Units not compatible for addition: {self.u} and {other.u}")
            raise e

        return type(self)(value=self.v * self.p + other.v * other.p, units=self.u.copy())

    def __radd__(self, other):
        try:
            other.u + self.u
        except AttributeError as e:
            logger.error(f"Unable to find units for addition: {other} and {self}.  Exception was: {e}")
            raise e
        except UnitsMissmatchException as e:
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
        try:
            if self.u != other.u:
                return False
        except AttributeError as e:
            if self.u == "1":
                logger.warning(f"Our units are '1' - trying scalar equals.  Using .value is prefered.")
                return self.value == other                
            logger.error(f"No units on other likely? Use .value to check scalar equality")
            raise TypeError(f"Unable to check equlity - no units on other? Acting on [{self}] == [{other}]")

        if self.v*self.p != other.v*other.p:
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
        return self.v*self.p.f

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

    Stored as numpy arrays internally

    A default value (var0) can be provided - this is used to calculate the quantity 
    value if no other points are given.

    When two dependant physical quanitites are acted on by a math operator, the left argument
    default value is retained.
    """
    __DEBUG = False

    @classmethod
    def from_string(cls, ustring):
        v, p, u = vpu_from_ustring(ustring)
        return cls(num=[v*p], den=[1], units=u)

    def __init__(self, num=None, den=None, units=None, 
                 var0=None, var_units="", var_symbol="x", 
                 tol=GLOBAL_TOLERANCE):
        """
        :param num: numerator array
        :param den: denominator array
        :param units: units as string or units class
        :param var0: default variable value - used when accessing value as scalars.
        :param var_units: variable units
        """
        super().__init__()
        self.u = Units.from_any(units)

        self.num = np.array(num if num is not None else [1])
        self.den = np.array(den if den is not None else [1])

        self.tol = tol

        if var0 is None:
            self._var0 = None
        elif isinstance(var0, PhysicalQuantity):
            self._var0 = var0
        else:
            self._var0 = PhysicalQuantity(value=var0, units=var_units)

        self._var_symbol = var_symbol

    def reduce_to_tol(self):
        """
        Removes all coefficients less than tolerance
        """
        self.num = np.where(abs(self.num) > self.tol, self.num, 0)
        self.den = np.where(abs(self.den) > self.tol, self.den, 0)

    def __repr__(self):
        try:
            v0 = self.var0
        except:
            v0 = "*"
        
        return f"[DPQ({v0}):({self.num})/({self.den}):({self.u})]"

    def __str__(self):
        try:
            v0 = str(self.var0.u)
        except:
            v0 = "*"
        self.reduce_to_tol()
        nps = polyprint(self.num, var=self._var_symbol)
        dps = polyprint(self.den, var=self._var_symbol)
        return f"f({self._var_symbol}[{v0}])[{str(self.u)}]=({nps})/({dps})"

    def __mul__(self, other):
        varargs = {"var0": None if self._var0 is None else self._var0,
                   "var_units": None if self._var0 is None else self._var0.u.copy()}
        
        if isinstance(other, DependantPhysicalQuantity):
            if self.__DEBUG: logger.error(f"MULT: as DPQs: {self} x {other}")            
            return type(self)(num=polymul(self.num, other.num), 
                              den=polymul(self.den, other.den),
                              units=self.u * other.u,
                              **varargs)
        
        else: #try scalar multiply
            return type(self)(num=self.num.copy()*other, den=self.den.copy(),
                              units=self.u.copy(), **varargs)

    def __rmul__(self, other):
        """
        same as __mul__
        """
        #TODO fill in to avoid another forwarded call
        return self*other

    def __sub__(self, other):
        try:
            self.u - other.u
        except AttributeError as e:
            logger.error(f"Unable to find units for subtraction: {self} and {other}.  Exception was: {e}")
            raise e
        except UnitsMissmatchException as e:
            logger.error(f"Units not compatible for subtraction: {self.u} and {other.u}")
            raise e
        
        if self.__DEBUG: logger.error(f"SUBS: as DPQs: {self} - {other}")

        # find common denom
        den = polymul(self.den, other.den)
        num_a = polymul(self.num, other.den) 
        num_b = polymul(self.den, other.num) 
        num = polysub(num_a, num_b)

        return type(self)(num=num, den=den,
                          units=self.u.copy(),
                          var0=self._var0.v, var_units=self._var0.u.copy(),
                          var_symbol=self._var_symbol)

    def __rsub__(self, other):
        try:
            other.u - self.u
        except AttributeError as e:
            logger.error(f"Unable to find units for operation: {other} and {self}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for subtraction: {other.u} and {self.u}")
            raise e

        if self.__DEBUG: logger.error(f"SUBS: as DPQs: {self} - {other}")

        # find common denom
        den = polymul(self.den, other.den)
        num_a = polymul(self.num, other.den) 
        num_b = polymul(self.den, other.num) 
        num = polysub(num_b, num_a)

        return type(self)(num=num, den=den,
                          units=self.u.copy(),
                          var0=self._var0.v, var_units=self._var0.u.copy(),
                          var_symbol=self._var_symbol)

    def __add__(self, other):
        try:
            self.u + other.u
        except AttributeError as e:
            logger.error(f"Unable to find units for addition: {self} and {other}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for addition: {self.u} and {other.u}")
            raise e

        if self.__DEBUG: logger.error(f"ADDS: as DPQs: {self} + {other}")

        # find common denom
        den = polymul(self.den, other.den)
        num_a = polymul(self.num, other.den) 
        num_b = polymul(self.den, other.num) 
        num = polyadd(num_a, num_b)

        return type(self)(num=num, den=den,
                          units=self.u.copy(),
                          var0=self._var0.v, var_units=self._var0.u.copy(),
                          var_symbol=self._var_symbol)

    def __radd__(self, other):
        try:
            other.u + self.u
        except AttributeError as e:
            logger.error(f"Unable to find units for addition: {other} and {self}.  Exception was: {e}")
            raise e
        except TypeError as e:
            logger.error(f"Units not compatible for addition: {other.u} and {self.u}")
            raise e

        return self + other

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __truediv__(self, other):
        if isinstance(other, DependantPhysicalQuantity):
            if self.__DEBUG: logger.error(f"DIVS: as DPQs: {self} / {other}")
            return type(self)(num=polymul(self.num, other.den), 
                              den=polymul(self.den, other.num),
                              units=self.u / other.u,
                              var0=self._var0.v, var_units=self._var0.u.copy())
        else: #try scalar multiply
            return type(self)(num=self.num.copy()/other, den=self.den.copy(),
                              units=self.u.copy(), var0=self._var0.copy())

    def __rtruediv__(self, other):
        if isinstance(other, DependantPhysicalQuantity):
            if self.__DEBUG: logger.error(f"RDIV: as DPQs: {other} / {self}")
            return type(self)(num=polymul(self.den, other.num), 
                              den=polymul(self.num, other.den),
                              units=other.u / self.u,
                              var0=self._var0.v, var_units=self._var0.u.copy())
        else: #try scalar div
            return type(self)(num=self.den.copy()*other, den=self.num.copy(),
                              units=1/self.u.copy(), var0=self._var0.copy()) 

    def __eq__(self, other):
        raise NotImplementedError("maybe write some code?")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __call__(self, var=None):
        """
        Evaluate dependant pysical quantity at given point(s)

        Returns a PhysicalQuantity (non dependant)
        """
        #TODO let this be called with physical quantities as input
        #TODO update to support input arrays

        if var is None:
            var = self.var0.value

        vn = polyeval(self.num, var)
        vd = polyeval(self.den, var)

        return PhysicalQuantity(value=vn/vd, units=self.u.copy())

    @property
    def var0(self):
        if self._var0 is None:
            raise ValueError("No initial value - was this ever set?")
        else:
            return self._var0

    @var0.setter
    def var0(self, val):
        if val is None: # easy case: unset what we had.
            self._var0 = None
        elif isinstance(val, PhysicalQuantity): # easy case: just set to new PQ
            self._var0 = val
        elif self._var0 is None:
            self._var0 = PhysicalQuantity(value=val)
        else:  # assume self._var0 is a PQ, and new item is not...
            self._var0 = PhysicalQuantity(value=val, units=self._var0.u) # type: ignore
