"""
Passive component types
"""

import logging

logger = logging.getLogger(__name__)

from abc import ABCMeta, abstractmethod
from pyee.types.physicalquantity import PhysicalQuantity
from pyee.types.prefixes import t_PrefixObj
from pyee.types.units import Units, t_UnitObj
from pyee.types.impedance import Impedance
from pyee.types.aliases import t_numeric
from pyee.types.converters import vp_from_number, vpu_from_ustring

from pyee.exceptions import UnitsMissmatchException

FREQUENCY_UNITS = "Hz"
ERROR_ON_Z_TRANSFORM = True

def set_error_on_z_transform(val):
    """
    If True, will raise an error on 
    operations that have non matching units.  If False, will
    quietly convert input to impedances and return result.
    """
    global ERROR_ON_Z_TRANSFORM
    ERROR_ON_Z_TRANSFORM = bool(val)

class PassiveComponent(PhysicalQuantity, metaclass=ABCMeta):
    @classmethod
    def from_string(cls, ustring: str, *args, **kwargs):
        """
        Create a PassiveComponent from a string
        :param ustring: string to parse
        :return: PassiveComponent instance
        """
        v, p, u = vpu_from_ustring(ustring)
        return cls(v, p, u, *args, **kwargs)

    @classmethod
    def from_value(cls, value: t_numeric, *args, **kwargs):
        """
        Create a PassiveComponent from a numeric value
        :param value: numeric value to use
        :return: PassiveComponent instance
        """
        v, p = vp_from_number(value)
        return cls(v, p, cls._UNITS, *args, **kwargs)

    def __init__(self, value:t_numeric, prefix:t_PrefixObj, units:t_UnitObj, *args, **kwargs) -> None:
        if (self.default_units is not None) and (units != self.default_units):
            if units.unitless:
                units = self.default_units.copy()
            else: # no units is OK - use default. if wrong units give... raise issue with it.
                try:
                    su = units.simplify()
                except AttributeError as _:
                    su = Units.create_unitless()
                
                if su != self.default_units:
                    raise UnitsMissmatchException(self.default_units, units, "init", 
                                                  notes=f"Creating new PassiveComponent with incorrect units... "
                                                  "started with {units}")
                else:
                    units = su
        super().__init__(value, prefix, units, *args, **kwargs)

    def __add__(self, value):
        try:
            return super().__add__(value)
        except UnitsMissmatchException as e:
            if ERROR_ON_Z_TRANSFORM:
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
            if ERROR_ON_Z_TRANSFORM:
                raise e
            logger.error(f"Ignoring units missmatch - trying to convert to impedances.")
        # convert to Z, and return
        thisZ = self.Z
        otherZ = value.Z
        return otherZ + thisZ 

    def __or__(self, other):
        try:
            nv = self * other / (self + other)
            return {"Ohm": lambda o: Resistor.from_value(value=o.v*o.p),
                    "F": lambda o: Capacitor.from_value(value=o.v*o.p),
                    "L": lambda o: Inductor.from_value(value=o.v*o.p)}.get(str(nv.u), lambda o: o)(nv)
        except (TypeError, AttributeError) as _:
            logger.warning(f"Unable to parallel natively - converting to impedance... {self} and {other}")
        
        sZ = self.Z
        oZ = other.Z
        return (sZ * oZ / (sZ + oZ))

    def __ror__(self, other):
        #TODO if units are the same on self and other, return correct passive type if possible
        try:
            nv = other * self / (other + self)
            return {"Ohm": lambda o: Resistor.from_value(value=o.v * o.p),
                    "F": lambda o: Capacitor.from_value(value=o.v * o.p),
                    "L": lambda o: Inductor.from_value(value=o.v * o.p)}.get(str(nv.u), lambda o: o)(nv)
        except (TypeError, AttributeError) as _:
            logger.warning(f"Unable to parallel natively - converting to impedance... {other} and {self}")
        
        oZ = other.Z
        sZ = self.Z
        return (oZ * sZ / (oZ + sZ))

    def __sub__(self, value):
        try:
            return super().__sub__(value)
        except UnitsMissmatchException as e:
            if ERROR_ON_Z_TRANSFORM:
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
            if ERROR_ON_Z_TRANSFORM:
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
    _UNITS = Units.from_string("Ohm")

    @property
    def Z(self):
        return Impedance(num=[self.v*self.p],den=[1], frequency_units=FREQUENCY_UNITS)
    
    @property
    def default_units(self) -> t_UnitObj:
        return self._UNITS

class Inductor(PassiveComponent):
    _UNITS = Units.from_string("H")

    @property
    def Z(self):
        return Impedance(num=[0, self.v * self.p], den=[1], frequency_units=FREQUENCY_UNITS)
    
    @property
    def default_units(self) -> t_UnitObj:
        return self._UNITS

class Capacitor(PassiveComponent):
    _UNITS = Units.from_string("F")

    @property
    def Z(self):
        return Impedance(num=[1],den=[0, self.v*self.p], frequency_units=FREQUENCY_UNITS)
    
    @property
    def default_units(self) -> t_UnitObj:
        return self._UNITS


