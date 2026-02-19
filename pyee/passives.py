"""
Passive component types
"""

import logging

logger = logging.getLogger(__name__)

from abc import ABCMeta, abstractmethod
from functools import singledispatchmethod

from pyee.types.physicalquantity import PhysicalQuantity
from pyee.types.prefixes import Prefix, t_PrefixObj
from pyee.types.units import Units, t_UnitObj
from pyee.types.impedance import Impedance
from pyee.types.aliases import t_numeric
from pyee.types.converters import vp_from_number, vpu_from_ustring

from pyee.exceptions import UnitsMissmatchException
from pyee import DEFAULT_FREQUENCY_UNITS, ERROR_ON_UNIT_MISSMATCH

class PassiveComponent(PhysicalQuantity, metaclass=ABCMeta):
    _UNITS = Units("") # placeholder - subs should overwrite.

    @singledispatchmethod
    def __init__(self, value:object, *args, **kwargs) -> None:
        raise ValueError(f"Cannot construct {type(self)} from {value} of type {type(value)}")

    @__init__.register(int | float)
    def _(self, value: t_numeric, *args, **kwargs) -> None:
        """
        Create a PassiveComponent from a numeric value.
        :param t_numeric value: numeric value to use
        :param str prefix: OPTIONAL units prefix to use.  If not specified, uses '1' (no prefix)
        :param any units: OPTIONAL units to use.  If not specified, uses the class default.
        :return: PassiveComponent instance
        """
        v, val_p = vp_from_number(value)
        
        arg_u = kwargs.pop("units", self.default_units.copy())
        if arg_u != self.default_units: # argument passed but it was incorrect...
            raise UnitsMissmatchException(self.default_units, arg_u, "init", 
                notes=f"Creating new PassiveComponent with incorrect units... started with {arg_u}")
        else: # argument passed... was correct... use it.
            u = arg_u

        arg_p = kwargs.pop("prefix", None)
        p = val_p*arg_p if arg_p is not None else val_p
        
        # Now have v, p, u.... can create a component.
        super().__init__(v, p, u, *args, **kwargs)

    @__init__.register(str)
    def _(self, value: str, *args, **kwargs) -> None:
        """
        Create a PassiveComponent from a string
        :param ustring: string to parse
        :param str prefix: OPTIONAL units prefix to use.  If not specified, uses '1' (no prefix)
        :param any units: OPTIONAL units to use.  If not specified, uses the class default.
        :return: PassiveComponent instance
        """
        v, val_p, val_u = vpu_from_ustring(value)
        arg_u = kwargs.pop("units", self.default_units.copy())

        if (not val_u.unitless) and (val_u != arg_u):
            raise UnitsMissmatchException(self.default_units, arg_u, "init", 
                notes=f"Creating new PassiveComponent, string had units {val_u}, "
                "but found units {arg_u} in arguments or from default. "
                "Check values!")

        if arg_u != self.default_units: # argument passed but it was incorrect...
            raise UnitsMissmatchException(self.default_units, arg_u, "init", 
                notes=f"Creating new PassiveComponent with incorrect units... started with {arg_u}")
        else: # argument passed and is fine... use it.
            u = arg_u

        arg_p = kwargs.pop("prefix", None)
        p = val_p*arg_p if arg_p is not None else val_p

        # Now have v, p, u.... can create a component.
        super().__init__(v, p, u, *args, **kwargs)

    def __add__(self, value):
        try:
            return super().__add__(value)
        except UnitsMissmatchException as e:
            if ERROR_ON_UNIT_MISSMATCH:
                raise e
            logger.error(f"Ignoring units missmatch - trying to convert to impedances.")
        # convert to Z, and return
        thisZ = self.Z
        otherZ = value.Z
        return thisZ + otherZ
    
    def __radd__(self, value):
        try:
            return super().__radd__(value)
        except UnitsMissmatchException as e:
            if ERROR_ON_UNIT_MISSMATCH:
                raise e
            logger.error(f"Ignoring units missmatch - trying to convert to impedances.")
        # convert to Z, and return
        thisZ = self.Z
        otherZ = value.Z
        return otherZ + thisZ 

    def __or__(self, other):
        try:
            nv = self * other / (self + other)
            return {"Ohm": lambda o: Resistor(o.v*o.p),
                    "F": lambda o: Capacitor(o.v*o.p),
                    "L": lambda o: Inductor(o.v*o.p)}.get(str(nv.u), lambda o: o)(nv)
        except (TypeError, AttributeError) as _:
            logger.warning(f"Unable to parallel natively - converting to impedance... {self} and {other}")
        
        sZ = self.Z
        oZ = other.Z
        return (sZ * oZ / (sZ + oZ))

    def __ror__(self, other):
        #TODO if units are the same on self and other, return correct passive type if possible
        try:
            nv = other * self / (other + self)
            return {"Ohm": lambda o: Resistor(o.v * o.p),
                    "F": lambda o: Capacitor(o.v * o.p),
                    "L": lambda o: Inductor(o.v * o.p)}.get(str(nv.u), lambda o: o)(nv)
        except (TypeError, AttributeError) as _:
            logger.warning(f"Unable to parallel natively - converting to impedance... {other} and {self}")
        
        oZ = other.Z
        sZ = self.Z
        return (oZ * sZ / (oZ + sZ))

    def __sub__(self, value):
        try:
            return super().__sub__(value)
        except UnitsMissmatchException as e:
            if ERROR_ON_UNIT_MISSMATCH:
                raise e
            logger.error(f"Ignoring units missmatch - trying to convert to impedances.")
        # convert to Z, and return
        thisZ = self.Z
        otherZ = value.Z
        return thisZ - otherZ
    
    def __rsub__(self, value):
        try:
            return super().__rsub__(value)
        except UnitsMissmatchException as e:
            if ERROR_ON_UNIT_MISSMATCH:
                raise e
            logger.error(f"Ignoring units missmatch - trying to convert to impedances.")
        # convert to Z, and return
        thisZ = self.Z
        otherZ = value.Z
        return otherZ - thisZ 

    @property
    @abstractmethod
    def Z(self) -> Impedance:
        """
        Impedance representation of this component
        :return: new Impedance instance
        """
        pass

    @property
    @abstractmethod
    def default_units(self) -> t_UnitObj:
        """
        Default units for new instances.
        """
        pass

class Resistor(PassiveComponent):
    _UNITS = Units("Ohm")

    @property
    def Z(self):
        return Impedance(num=[self.v*self.p],den=[1], frequency_units=DEFAULT_FREQUENCY_UNITS)
    
    @property
    def default_units(self) -> t_UnitObj:
        return self._UNITS

class Inductor(PassiveComponent):
    _UNITS = Units("H")

    @property
    def Z(self):
        return Impedance(num=[0, self.v * self.p], den=[1], frequency_units=DEFAULT_FREQUENCY_UNITS)
    
    @property
    def default_units(self) -> t_UnitObj:
        return self._UNITS

class Capacitor(PassiveComponent):
    _UNITS = Units("F")

    @property
    def Z(self):
        return Impedance(num=[1],den=[0, self.v*self.p], frequency_units=DEFAULT_FREQUENCY_UNITS)
    
    @property
    def default_units(self) -> t_UnitObj:
        return self._UNITS
