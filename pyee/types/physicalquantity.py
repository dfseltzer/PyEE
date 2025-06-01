"""
Physical Quantity  and derived classes
"""

import numpy as np

import logging
import copy

from abc import ABC
from abc import abstractmethod

from pyee.types.units import Units, t_UnitObj, t_UnitsSource

from pyee.types.prefixes import t_PrefixObj
from pyee.types.converters import vpu_from_ustring
from pyee.types.converters import vp_from_number

from pyee.types.aliases import t_numeric
from pyee.types.aliases import t_listTuple

from pyee import GLOBAL_TOLERANCE

from pyee.math.polynomials import polyeval
from pyee.math.polynomials import polymul
from pyee.math.polynomials import polyadd
from pyee.math.polynomials import polyprint
from pyee.math.polynomials import polysub

from pyee.exceptions import UnitsMissmatchException

type t_PQSource = PhysicalQuantity | t_numeric | str
type t_PQBObj = PhysicalQuantityBase
type t_PQObj = PhysicalQuantity
type t_DPQObj = DependantPhysicalQuantity

logger = logging.getLogger(__name__)

ERROR_ON_UNITLESS_OPERATORS = False

class PhysicalQuantityBase(ABC):

    @classmethod
    @abstractmethod
    def from_string(cls, ustring, **kwargs) -> t_PQBObj:
        pass

    @classmethod
    @abstractmethod
    def from_value(cls, *args, **kwargs) -> t_PQBObj:
        pass

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    @abstractmethod
    def __copy__(self) -> t_PQBObj:
        pass

class PhysicalQuantity(PhysicalQuantityBase):
    __DEBUG = False

    @classmethod
    def from_string(cls, ustring:str, **kwargs) -> t_PQObj:
        """
        Create a new Physical Quantity from a unit string.
        """
        if cls.__DEBUG: logger.error(f"Creating PQ from ustring={ustring}")
        (v, p, u) = vpu_from_ustring(ustring)
        return cls(v, p, u, **kwargs)

    @classmethod
    def from_value(cls, value:t_numeric , units:t_UnitsSource, **kwargs) -> t_PQObj:
        """
        Create a new Physical Quantity from a value and optional unit.
        """
        if cls.__DEBUG: logger.error(f"Creating PQ from value={value}, units={units}")
        v, p = vp_from_number(value)
        u = Units.from_any(units)
        return cls(v, p, u, **kwargs)

    @classmethod
    def from_any(cls, value:t_PQSource) -> t_PQObj:
        if isinstance(value, PhysicalQuantity):
            return value.copy()
        elif isinstance(value, str):
            return cls.from_string(value)
        else: # try from value... might work?
            return cls.from_value(value, units=None)

    def __init__(self, value:t_numeric, prefix:t_PrefixObj, units:t_UnitObj) -> None:
        """
        Use constructors from_value and from_string!
        """
        super().__init__()
        self.v = value
        self.p = prefix
        self.u = units

    def __copy__(self) -> t_PQObj:
        nv = self.v # value is a number, no need to copy it
        np = self.p.copy() # prefix object - needs copy
        nu = self.u.copy() # units is an object - needs a copy
        return type(self)(nv, np, nu)

    def __repr__(self):
        return f"{self.v:7.3f}{self.p} [{self.u}]"

    def __mul__(self, other):
        if isinstance(other, PhysicalQuantity):
            nv, np = vp_from_number(self.v*self.p.f*other.v*other.p.f)
            nu = self.u*other.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to multiply - no units on other? Acting on [{self}] * [{other}]")
        else: #try scalar multiply
            nv, np = vp_from_number(self.v*self.p*other)
            nu = self.u
        return PhysicalQuantity(nv, np, nu)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        if isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="sub")
            nv, np = vp_from_number(self.v*self.p - other.v*other.p) #type: ignore
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to subtract - no units on other? Acting on [{self}] - [{other}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for subtraction: {self} - {other}")
            nv, np = vp_from_number(self.v*self.p - other)
        return PhysicalQuantity(value=nv, prefix=np, units=self.u)

    def __rsub__(self, other):
        if isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="rsub")
            nv, np = vp_from_number(other.v*other.p - self.v*self.p) #type: ignore
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to subtract - no units on other? Acting on [{other}] - [{self}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for subtraction: {other} - {self}")
            nv, np = vp_from_number(other - self.v*self.p)
        return PhysicalQuantity(value=nv, prefix=np, units=self.u)

    def __add__(self, other):
        if isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="add")
            nv, np = vp_from_number(self.v*self.p + other.v*other.p) #type: ignore
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to add - no units on other? Acting on [{self}] + [{other}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for addition: {self} + {other}")
            nv, np = vp_from_number(self.v*self.p + other)
        return PhysicalQuantity(value=nv, prefix=np, units=self.u)

    def __radd__(self, other):
        return self.__add__(other)

    def __truediv__(self, other):
        if isinstance(other, PhysicalQuantity):
            #if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="div")
            nv, np = vp_from_number(self.v*self.p.f/(other.v*other.p.f))
            nu = self.u/other.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to divide - no units on other? Acting on [{self}] / [{other}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for division: {self}/{other}")
            nv, np = vp_from_number((self.v*self.p)/other)
            nu = self.u
        return PhysicalQuantity(value=nv, prefix=np, units=nu)

    def __rtruediv__(self, other):
        if isinstance(other, PhysicalQuantity):
            #if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="rdiv")
            nv, np = vp_from_number(other.v*other.p.f/(self.v*self.p.f))
            nu = other.u/self.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to divide - no units on other? Acting on [{other}] / [{self}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for rdivision: {other}/{self}")
            logger.warning(f"self units... {self.u}")
            nv, np = vp_from_number(other/(self.v*self.p))
            nu = 1/self.u
        return PhysicalQuantity(value=nv, prefix=np, units=nu)

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __eq__(self, other):
        if isinstance(other, PhysicalQuantity):
            if self.u != other.u:
                return False
            else:
                return self.v*self.p == other.v*other.p
        elif self.u == "1":
            return self.v*self.p == other
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to check equlity - no units on other? Acting on [{self}] == [{other}]")
        else:
            logger.warning(f"Assuming units for equality: {self} == {other}")
            return self.v*self.p == other

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def value(self):
        """
        :return: value as a scalar
        """
        return self.v*self.p.f
    
    @value.setter
    def value(self, val):
        self.v, self.p = vp_from_number(val)

    @property
    def units(self):
        return self.u

    @units.setter
    def units(self, val: t_UnitsSource):
        newunits = Units.from_any(val)
        if not self.u.unitless:
            convfunc = self.u.convert_to(newunits)
            newval = convfunc(self.v*self.p)
            self.v, self.p = vp_from_number(newval)
        self.u = newunits    

    def as_base(self, **kwargs) -> t_PQObj:
        """
        converts units to base units in given context

        :return: new Physical Quantities instance in base units
        """

        newunits = self.u.as_base(**kwargs)
        return PhysicalQuantity(value=self.v, prefix=self.p.copy(), units=newunits)

    def copy(self) -> t_PQObj:
        return self.__copy__()

    def simplify(self, **kwargs) -> t_PQObj:
        newunits = self.u.simplify(**kwargs)
        return PhysicalQuantity(value=self.v, prefix=self.p, units=newunits)


class DependantPhysicalQuantity(PhysicalQuantityBase):
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
    def from_string(cls, ustring : str, **kwargs) -> t_DPQObj:
        raise NotImplementedError(f"Not done yet... cant turn {ustring} into dependant.  Write some code maybe?")
    
    @classmethod
    def from_value(cls, num : t_listTuple | np.ndarray | None, 
                   den : t_listTuple | np.ndarray | None = None, 
                   units : t_UnitsSource = None, 
                   var0 : "PhysicalQuantity | t_numeric | None" = None, 
                   var_units=None, 
                   **kwargs) -> t_DPQObj:
        """
        :param num: numerator array
        :param den: denominator array, or None (if demoninator = 1)
        :param units: units as string or units class (optional)
        :param var0: default variable value - used when accessing value as scalars.
        :param var_units: variable units
        """
        n = np.array(num if num is not None else [1])
        d = np.array(den if den is not None else [1])
        u = Units.from_any(units)

        vu = Units.from_any(var_units)

        return cls(num=n, den=d, units=u,
                   var0=var0, var_units=vu,
                   **kwargs)

    def __init__(self, num : t_listTuple | np.ndarray | None = None, 
                 den: t_listTuple | np.ndarray | None = None, 
                 units : t_UnitsSource | None = None, 
                 var0: t_numeric | PhysicalQuantity | None=None, 
                 var_units : t_UnitsSource| None=None, 
                 var_symbol: str = "x", 
                 tol: float=GLOBAL_TOLERANCE):
        """
        :param num: numerator array
        :param den: denominator array
        :param units: units as string or units class
        :param var0: default variable value - used when accessing value as scalars.
        :param var_units: variable units
        """
        super().__init__()
        self.u = Units.from_any(units)

        self.num = np.array(num)
        self.den = np.array(den)
        self.tol = tol

        if var0 is None:
            self._var0 = None
        elif isinstance(var0, PhysicalQuantity):
            self._var0 = var0
        else: # try it... might work?
            self._var0 = PhysicalQuantity.from_value(value=var0, units=var_units)                
        self._var_symbol = var_symbol

    def __copy__(self) -> t_DPQObj:
        return type(self)(num=self.num.copy(),
                          den=self.den.copy(),
                          units=self.u.copy(),
                          var0=self._var0,
                          var_symbol=self._var_symbol, 
                          tol=self.tol)

    def __repr__(self):
        try:
            v0 = self.var0
        except:
            v0 = "*"
        
        return f"[DPQ({v0}):({tuple(self.num)})/({tuple(self.den)}):({self.u})]"

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
        if self.__DEBUG: logger.error(f"MULT: as DPQs: {self} x {other}")   
        if isinstance(other, DependantPhysicalQuantity):
            nn = polymul(self.num, other.num)
            nd = polymul(self.den, other.den)
            nu = self.u * other.u
        elif isinstance(other, PhysicalQuantity):
            nn = self.num*other.v*other.p.f
            nd = self.den.copy()
            nu = self.u * other.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to multiply - no units on other? Acting on [{self}] * [{other}]")
        else: #try scalar multiply
            nn = self.num.copy()*other
            nd = self.den.copy()
            nu = self.u.copy() # do we need the copy?
        return DependantPhysicalQuantity(num=nn, den=nd, units=nu, **varargs)

    def __rmul__(self, other):
        # same implementation as mul... no difference...
        varargs = {"var0": None if self._var0 is None else self._var0,
                   "var_units": None if self._var0 is None else self._var0.u.copy()}
        if isinstance(other, DependantPhysicalQuantity):
            if self.__DEBUG: logger.error(f"MULT: as DPQs: {self} x {other}")   
            nn = polymul(self.num, other.num)
            nd = polymul(self.den, other.den)
            nu = self.u * other.u
        elif isinstance(other, PhysicalQuantity):
            nn = self.num*other.v*other.p.f
            nd = self.den.copy()
            nu = self.u * other.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to multiply - no units on other? Acting on [{other}] * [{self}]")
        else: #try scalar multiply
            nn = self.num.copy()*other
            nd = self.den.copy()
            nu = self.u.copy() # do we need the copy?
        return DependantPhysicalQuantity(num=nn, den=nd, units=nu, **varargs)

    def __sub__(self, other):
        varargs = {"var0": None if self._var0 is None else self._var0,
                   "var_units": None if self._var0 is None else self._var0.u.copy()}
        if isinstance(other, DependantPhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="sub")
            nd = polymul(self.den, other.den)
            num_a = polymul(self.num, other.den) 
            num_b = polymul(self.den, other.num) 
            nn = polysub(num_a, num_b)
            nu = self.u.copy()
        elif isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="sub")
            nd = self.den.copy() # type: ignore
            num_a = self.num
            num_b = self.den*other.v*other.p #type: ignore
            nn = polysub(num_a, num_b)
            nu = self.u.copy()
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to subtract - no units on other? Acting on [{self}] - [{other}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for subtraction: {self} - {other}")
            nd = self.den.copy() # type: ignore
            num_a = self.num
            num_b = self.den*other #type: ignore
            nn = polysub(num_a, num_b)
            nu = self.u.copy()
        return DependantPhysicalQuantity(num=nn, den=nd, units=nu, **varargs)

    def __rsub__(self, other):
        varargs = {"var0": None if self._var0 is None else self._var0,
                   "var_units": None if self._var0 is None else self._var0.u.copy()}
        if isinstance(other, DependantPhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=other.u, u2=self.u, operation="rsub")
            nd = polymul(self.den, other.den)
            num_a = polymul(self.num, other.den) 
            num_b = polymul(self.den, other.num) 
            nn = polysub(num_b, num_a)
            nu = self.u.copy()
        elif isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=other.u, u2=self.u, operation="rsub")
            nd = self.den.copy() # type: ignore
            num_a = self.num
            num_b = self.den*other.v*other.p #type: ignore
            nn = polysub(num_b, num_a)
            nu = self.u.copy()
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to subtract - no units on other? Acting on [{other}] - [{self}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for subtraction: {other} - {self}")
            nd = self.den.copy() # type: ignore
            num_a = self.num
            num_b = self.den*other #type: ignore
            nn = polysub(num_b, num_a)
            nu = self.u.copy()
        return DependantPhysicalQuantity(num=nn, den=nd, units=nu, **varargs)

    def __add__(self, other):
        varargs = {"var0": None if self._var0 is None else self._var0,
                   "var_units": None if self._var0 is None else self._var0.u.copy()}
        if isinstance(other, DependantPhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="add")
            nd = polymul(self.den, other.den)
            num_a = polymul(self.num, other.den) 
            num_b = polymul(self.den, other.num) 
            nn = polyadd(num_a, num_b)
            nu = self.u.copy()
        elif isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="add")
            nd = self.den.copy() # type: ignore
            num_a = self.num
            num_b = self.den*other.v*other.p #type: ignore
            nn = polyadd(num_a, num_b)
            nu = self.u.copy()
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to add - no units on other? Acting on [{self}] + [{other}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for addition: {self} + {other}")
            nd = self.den.copy() # type: ignore
            num_a = self.num
            num_b = self.den*other #type: ignore
            nn = polyadd(num_a, num_b)
            nu = self.u.copy()
        return DependantPhysicalQuantity(num=nn, den=nd, units=nu, **varargs)

    def __radd__(self, other):
        varargs = {"var0": None if self._var0 is None else self._var0,
                   "var_units": None if self._var0 is None else self._var0.u.copy()}
        if isinstance(other, DependantPhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=other.u, u2=self.u, operation="radd")
            nd = polymul(self.den, other.den)
            num_a = polymul(self.num, other.den) 
            num_b = polymul(self.den, other.num) 
            nn = polyadd(num_b, num_a)
            nu = self.u.copy()
        elif isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=other.u, u2=self.u, operation="radd")
            nd = self.den.copy() # type: ignore
            num_a = self.num
            num_b = self.den*other.v*other.p #type: ignore
            nn = polyadd(num_b, num_a)
            nu = self.u.copy()
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to subtract - no units on other? Acting on [{other}] + [{self}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for raddition: {other} + {self}")
            nd = self.den.copy() # type: ignore
            num_a = self.num
            num_b = self.den*other #type: ignore
            nn = polyadd(num_b, num_a)
            nu = self.u.copy()
        return DependantPhysicalQuantity(num=nn, den=nd, units=nu, **varargs)

    def __truediv__(self, other):
        varargs = {"var0": None if self._var0 is None else self._var0,
                   "var_units": None if self._var0 is None else self._var0.u.copy()}
        if isinstance(other, DependantPhysicalQuantity):
            #if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="div")
            nn = polymul(self.num, other.den)
            nd = polymul(self.den, other.num)
            nu = self.u/other.u
        elif isinstance(other, PhysicalQuantity):
            #if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="div")
            nn = self.num.copy() #type: ignore
            nd = self.den*(other.v*other.p)
            nu = self.u/other.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to divide - no units on other? Acting on [{self}] / [{other}]")
        else: # try as scalar? Assuming units..
            logger.warning(f"Assuming units for division: {self} / {other}")
            nn = self.num.copy() #type: ignore
            nd = self.den*(other)
            nu = self.u/other.u
        return DependantPhysicalQuantity(num=nn, den=nd, units=nu, **varargs)

    def __rtruediv__(self, other):
        varargs = {"var0": None if self._var0 is None else self._var0,
                   "var_units": None if self._var0 is None else self._var0.u.copy()}
        if isinstance(other, DependantPhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=other.u, u2=self.u, operation="rdiv")
            nn = polymul(other.num, self.den)
            nd = polymul(other.den, self.num)
            nu = other.u/self.u
        elif isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=other.u, u2=self.u, operation="rdiv")
            nn = self.den.copy()*(other.v*other.p) #type: ignore
            nd = self.num.copy() #type: ignore
            nu = other.u/self.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to divide - no units on other? Acting on [{other}] / [{self}]")
        else: # try as scalar? Assuming units..
            nn = self.den.copy()*(other) #type: ignore
            nd = self.num.copy() #type: ignore
            logger.warning(f"Inverting Units: self.u={self.u}")
            nu = 1/self.u
        return DependantPhysicalQuantity(num=nn, den=nd, units=nu, **varargs)

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __eq__(self, other):
        raise NotImplementedError("maybe write some code?")

    def __ne__(self, other):
        return not self.__eq__(other)

    def __call__(self, var=None) -> "PhysicalQuantity":
        """
        Evaluate dependant pysical quantity at given point(s)

        Returns a PhysicalQuantity (non dependant)
        """

        if (var is None) and (self.var0 is None):
            raise ValueError("Unable to call dependant physical quantity: No value given, and var0 is NONE")
        var = self.var0 if var is None else var

        if isinstance(var, PhysicalQuantity):
            if (self.var0 is not None) and (self.var0.u != var.u):
                raise UnitsMissmatchException(u1=self.var0.u, u2=var.u, operation="call",
                                              notes=f"DPQ[{self}] expects input with units {self.var0.u}, but input had units {var.u}")
            elif ERROR_ON_UNITLESS_OPERATORS:
                raise TypeError(f"Unable to call - unknown variable units (got {var}). Set var0 to something!")
            else:
                logger.warning(f"unable to check units on call: no var0(={self.var0}) set? got {var}")
            val = var.v*var.p.f
        elif ERROR_ON_UNITLESS_OPERATORS:
                raise TypeError(f"Unable to call - unknown variable units (got {var}). Set var0 to something!")
        else: # assume scalar and try it...
            val = var

        vn = polyeval(self.num, val)
        vd = polyeval(self.den, val)

        # currently should fail if vn or vd have more than one element... ignore types trying to tell us that
        return PhysicalQuantity.from_value(vn/vd, self.u.copy()) #type: ignore

    @property
    def var0(self):
        if self._var0 is None:
            raise ValueError("No initial value - was this ever set?")
        else:
            return self._var0

    @var0.setter
    def var0(self, val : None | PhysicalQuantity | t_numeric):
        if val is None: # easy case: unset what we had.
            self._var0 = None
        elif isinstance(val, PhysicalQuantity): # easy case: just set to new PQ
            self._var0 = val
        elif self._var0 is None:
            nv, np = vp_from_number(val)
            nu = Units.create_unitless()
            self._var0 = PhysicalQuantity(value=nv, prefix=np, units=nu)
        else:  # assume self._var0 is a PQ, and new item is not...
            nv, np = vp_from_number(val)
            self._var0 = PhysicalQuantity(value=nv, prefix=np, units=self._var0.u) # type: ignore

    def reduce_to_tol(self):
        """
        Removes all coefficients less than tolerance
        """
        self.num = np.where(abs(self.num) > self.tol, self.num, 0) #type: ignore
        self.den = np.where(abs(self.den) > self.tol, self.den, 0) #type: ignore