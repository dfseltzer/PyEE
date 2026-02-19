"""
Physical Quantity  and derived classes
"""

import numpy as np

import logging
import numbers

from abc import ABCMeta
from abc import abstractmethod

from pyee.types.units import Units, t_UnitObj, t_UnitsSource

from pyee.types.prefixes import t_PrefixObj
from pyee.types.converters import vpu_from_ustring
from pyee.types.converters import vp_from_number

from pyee.types.aliases import t_numeric
from pyee.types.aliases import t_listTuple

from pyee import GLOBAL_TOLERANCE, ERROR_ON_UNITLESS_OPERATORS

from pyee.math.polynomials import polyeval, polymul, polyadd, polyprint, polysub
from pyee.exceptions import UnitsMissmatchException

type t_PQSource = PhysicalQuantity | t_numeric | str
type t_PQBObj = PhysicalQuantityBase
type t_PQObj = PhysicalQuantity
type t_DPQObj = DependantPhysicalQuantity

logger = logging.getLogger(__name__)

def value_from_any(inobj):
    """
    Returns a scalar value, given either a physical quantity or a value
    """
    if isinstance(inobj, (int, numbers.Number)):
        return inobj
    
    try:
        return inobj.value
    except Exception as e:
        raise ValueError(f"Unable to convert {inobj}(type: {type(inobj)}) to a numeric.") from e

class PhysicalQuantityBase(object, metaclass=ABCMeta):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()

    def copy(self) -> t_PQBObj:
        return self.__copy__()

    @abstractmethod
    def simplify(self, **kwargs) -> t_PQBObj:
        pass

    @abstractmethod
    def __copy__(self) -> t_PQBObj:
        pass


class PhysicalQuantity(PhysicalQuantityBase):
    __DEBUG = False

    @singledispatchmethod
    def __init__(self, value: object, units: t_UnitsSource = None, **kwargs) -> None:
        """
        Constructs a PhysicalQuantity from various sources.

        This constructor uses singledispatch to handle different input types for the 'value' argument.
        - For numeric types (int, float), it creates a PhysicalQuantity, using the 'units' kwarg.
        - For string types, it parses the string (e.g., "10k Ohm") to determine value, prefix, and units.
        - For another PhysicalQuantity, it creates a copy.

        When constructed using numeric or string types, an optional prefix argument can always
        be supplied.  For instance, PhysicalQuantity(0.01, prefix="u", units="F") could be used
        to represent 0.01uF, or 10nF equivilently.

        :param value: The value to initialize from (numeric, string, or another PhysicalQuantity).
        :param units: The units to associate with the value. Primarily used for numeric inputs.
        """
        raise TypeError(f"Cannot construct PhysicalQuantity from type {type(value)}")

    @__init__.register(int)
    @__init__.register(float)
    def _(self, value: t_numeric, units: t_UnitsSource = None, **kwargs) -> None:
        v, val_p = vp_from_number(value)
        arg_p = kwargs.get("prefix", None)

        # Combine the prefix from the value with the argument prefix, if provided
        p = val_p * arg_p if arg_p is not None else val_p

        # Rebalance the value based on the final prefix
        self.v = value / p.f
        self.p = p
        self.u = Units(units)
    
    @__init__.register(str)
    def _(self, value: str, units: t_UnitsSource = None, **kwargs) -> None:
        v, val_p, val_u = vpu_from_ustring(value)
        arg_p = kwargs.get("prefix", None)

        # Combine prefix from the string with the argument prefix
        self.p = val_p * arg_p if arg_p is not None else val_p
        self.v = v
        # The units kwarg overrides units found in the string
        self.u = Units(units) if units is not None else val_u

    def __copy__(self) -> t_PQObj:
        nv = self.v # value is a number, no need to copy it
        np = self.p.copy() # prefix object - needs copy
        nu = self.u.copy() # units is an object - needs a copy
        return type(self)(nv, units=nu)

    def __repr__(self):
        return f"{self.v:7.3f}{self.p} [{self.u}]"

    def __mul__(self, other):
        if isinstance(other, PhysicalQuantity):
            nv, np = vp_from_number(self.v*self.p.f*other.v*other.p.f)
            nu = self.u*other.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to multiply - no units on other? Acting on [{self}] * [{other}]")
        else: #try scalar multiply
            nv, np = vp_from_number(self.value*other)
            nu = self.u.copy()
        return PhysicalQuantity(nv, units=nu)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __sub__(self, other):
        if isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="sub")
            nv, np = vp_from_number(self.v*self.p - other.v*other.p) #type: ignore
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to subtract - no units on other? Acting on [{self}] - [{other}]")
        else: # try as scalar? Assuming units..
            logger.debug(f"Assuming units for subtraction: {self} - {other}")
            nv, np = vp_from_number(self.value - other)
        return PhysicalQuantity(nv, np, self.u)

    def __rsub__(self, other):
        if isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="rsub")
            nv, np = vp_from_number(other.v*other.p - self.v*self.p) #type: ignore
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to subtract - no units on other? Acting on [{other}] - [{self}]")
        else: # try as scalar? Assuming units..
            logger.debug(f"Assuming units for subtraction: {other} - {self}")
            nv, np = vp_from_number(other - self.value)
        return PhysicalQuantity(nv, np, self.u)

    def __add__(self, other):
        if isinstance(other, PhysicalQuantity):
            if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="add")
            nv, np = vp_from_number(self.v*self.p + other.v*other.p) #type: ignore
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to add - no units on other? Acting on [{self}] + [{other}]")
        else: # try as scalar? Assuming units..
            logger.debug(f"Assuming units for addition: {self} + {other}")
            nv, np = vp_from_number(self.value + other)
        return PhysicalQuantity(nv, np, self.u)

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
            logger.debug(f"Assuming units for division: {self}/{other}")
            nv, np = vp_from_number(self.value/other) # type: ignore
            nu = self.u.copy()
        return PhysicalQuantity(nv, units=nu)

    def __rtruediv__(self, other):
        if isinstance(other, PhysicalQuantity):
            #if self.u != other.u: raise UnitsMissmatchException(u1=self.u, u2=other.u, operation="rdiv")
            nv, np = vp_from_number(other.v*other.p.f/(self.v*self.p.f))
            nu = other.u/self.u
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to divide - no units on other? Acting on [{other}] / [{self}]")
        else: # try as scalar? Assuming units..
            logger.debug(f"Assuming units for rdivision: {other}/{self}")
            logger.debug(f"self units... {self.u}")
            nv, np = vp_from_number(other/self.value)
            nu = 1/self.u # type: ignore
        return PhysicalQuantity(nv, units=nu)

    def __div__(self, other):
        return self.__truediv__(other)

    def __rdiv__(self, other):
        return self.__rtruediv__(other)

    def __eq__(self, other):
        if isinstance(other, PhysicalQuantity):
            if self.u != other.u:
                return False
            else:
                return self.value == other.value
        elif self.u == "1":
            return self.value == other
        elif ERROR_ON_UNITLESS_OPERATORS: # try as scalar? Assuming units..
            raise TypeError(f"Unable to check equlity - no units on other? Acting on [{self}] == [{other}]")
        else:
            logger.warning(f"Assuming units for equality: {self} == {other}")
            return self.value == other

    def __ne__(self, other):
        return not self.__eq__(other)

    def __array__(self, dtype=None, copy=None):
        # Numpy array compatability stuff...
        if copy is False:
            logger.error(f"Cannot pass copy=false... will always copy.")
        return np.array(self.value)

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
        newunits = Units(val)
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
        return PhysicalQuantity(self.value, units=newunits)

    def simplify(self, **kwargs) -> t_PQObj:
        newunits = self.u.simplify(**kwargs)
        return PhysicalQuantity(self.value, units=newunits)


@PhysicalQuantity.__init__.register(PhysicalQuantity)
def _(self, value: t_PQObj, units: t_UnitsSource = None, **kwargs) -> None:
    """Creates a copy of another PhysicalQuantity."""
    self.v, self.p, self.u = value.v, value.p.copy(), value.u.copy()

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
        u = Units(units)

        vu = Units(var_units)

        return cls(num=n, den=d, units=u,
                   var0=var0, var_units=vu,
                   **kwargs)

    def __init__(self, num : t_listTuple | np.ndarray | None = None, 
                 den: t_listTuple | np.ndarray | None = None, 
                 units : t_UnitsSource | None = None, 
                 var0: t_numeric | PhysicalQuantity | None=None, 
                 var_units : t_UnitsSource| None=None, 
                 var_symbol: str = "x", 
                 tol=GLOBAL_TOLERANCE) -> None:
        """
        :param num: numerator array
        :param den: denominator array
        :param units: units as string or units class
        :param var0: default variable value - used when accessing value as scalars.
        :param var_units: variable units
        """
        super().__init__()
        self.u = Units(units)

        self.num = np.array(num)
        self.den = np.array(den)
        self.tol = tol

        if var0 is None:
            self._var0 = None
        elif isinstance(var0, PhysicalQuantity):
            self._var0 = var0
        else: # try it... might work?
            self._var0 = PhysicalQuantity(value=var0, units=var_units)                
        self._var_symbol = var_symbol

    def __copy__(self) -> t_DPQObj:
        return type(self)(num=self.num.copy(),
                          den=self.den.copy(),
                          units=self.u.copy(),
                          var0=self._var0.copy() if self._var0 is not None else None, # type: ignore
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
            logger.debug(f"Assuming units for subtraction: {self} - {other}")
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
            logger.debug(f"Assuming units for subtraction: {other} - {self}")
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
            logger.debug(f"Assuming units for addition: {self} + {other}")
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
            logger.debug(f"Assuming units for raddition: {other} + {self}")
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
            logger.debug(f"Assuming units for division: {self} / {other}")
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
            logger.debug(f"Inverting Units: self.u={self.u}")
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
        return PhysicalQuantity(vn/vd, units=self.u.copy()) #type: ignore

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
            nu = Units()
            self._var0 = PhysicalQuantity(nv, units=nu)
        else:  # assume self._var0 is a PQ, and new item is not...
            nv, np = vp_from_number(val)
            self._var0 = PhysicalQuantity(nv, units=self._var0.u) # type: ignore

    def copy(self) -> t_DPQObj:
        return self.__copy__()

    def simplify(self, **kwargs) -> t_DPQObj:
        newobj = self.copy()
        newobj.u = self.u.simplify(**kwargs)
        newobj._var0 = self._var0.copy() if self._var0 is not None else None
        newobj.reduce_to_tol()  
        return newobj

    def reduce_to_tol(self):
        """
        Removes all coefficients less than tolerance
        """
        self.num = np.where(abs(self.num) > self.tol, self.num, 0) #type: ignore
        self.den = np.where(abs(self.den) > self.tol, self.den, 0) #type: ignore