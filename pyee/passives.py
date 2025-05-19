"""
Passive component types
"""

import logging

logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod
from .types.physicalquantity import PhysicalQuantity
from .types.impedance import Impedance

from .exceptions import UnitsMissmatchException

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

class PassiveComponent(ABC, PhysicalQuantity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            return {"Ohm": lambda o: Resistor(value=o.v*o.p),
                    "F": lambda o: Capacitor(value=o.v*o.p),
                    "L": lambda o: Inductor(value=o.v*o.p)}.get(str(nv.u), lambda o: o)(nv)
        except (TypeError, AttributeError) as _:
            logger.warning(f"Unable to parallel natively - converting to impedance... {self} and {other}")
        
        sZ = self.Z
        oZ = other.Z
        return (sZ * oZ / (sZ + oZ))

    def __ror__(self, other):
        #TODO if units are the same on self and other, return correct passive type if possible
        try:
            nv = other * self / (other + self)
            return {"Ohm": lambda o: Resistor(value=o.v * o.p),
                    "F": lambda o: Capacitor(value=o.v * o.p),
                    "L": lambda o: Inductor(value=o.v * o.p)}.get(str(nv.u), lambda o: o)(nv)
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

class Resistor(PassiveComponent):
    def __init__(self, value, **kwargs):
        super().__init__(value=value, units=kwargs.pop("units","Ohm"))

    @property
    def Z(self):
        return Impedance(num=[self.v*self.p],den=[1], frequency_units=FREQUENCY_UNITS)

class Inductor(PassiveComponent):
    def __init__(self, value, **kwargs):
        super().__init__(value=value, units=kwargs.pop("units","H"))

    @property
    def Z(self):
        return Impedance(num=[0, self.v * self.p], den=[1], frequency_units=FREQUENCY_UNITS)

class Capacitor(PassiveComponent):
    def __init__(self, value, **kwargs):
        super().__init__(value=value, units=kwargs.pop("units","F"))

    @property
    def Z(self):
        return Impedance(num=[1],den=[0, self.v*self.p], frequency_units=FREQUENCY_UNITS)


