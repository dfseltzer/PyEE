"""
Passive component types
"""

import logging

logger = logging.getLogger(__name__)

from abc import ABC, abstractmethod
from .types.pq import PhysicalQuantity
from .types.impedance import Impedance

FREQUENCY_UNITS = "Hz"

class PassiveComponent(ABC, PhysicalQuantity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # add parallel operation
    def __or__(self, other):
        try:
            nv = self * other / (self + other)
            return {"Ohm": lambda o: Resistor(value=o.v*o.p),
                    "F": lambda o: Capacitor(value=o.v*o.p),
                    "L": lambda o: Inductor(value=o.v*o.p)}.get(str(nv.u), lambda o: o)(nv)
        except TypeError:
            logger.warning(f"Unable to parallel natively - converting to impedance... {self} and {other}")
            sZ = self.Z
            oZ = other.Z
            return sZ * oZ / (sZ + oZ)

    def __ror__(self, other):
        #TODO if units are the same on self and other, return correct passive type if possible
        try:
            nv = other * self / (other + self)
            return {"Ohm": lambda o: Resistor(value=o.v * o.p),
                    "F": lambda o: Capacitor(value=o.v * o.p),
                    "L": lambda o: Inductor(value=o.v * o.p)}.get(str(nv.u), lambda o: o)(nv)
        except TypeError:
            logger.warning(f"Unable to parallel natively - converting to impedance... {other} and {self}")
            oZ = other.Z
            sZ = self.Z
            return oZ * sZ / (oZ + sZ)

    @property
    @abstractmethod
    def Z(self):
        """
        Impedance representation of this component
        :return: new Impedance instance
        """
        pass

class Resistor(PassiveComponent):
    def __init__(self, value, **kwargs):
        super().__init__(value=value, units="Ohm")

    @property
    def Z(self):
        return Impedance(num=[self.v*self.p],den=[1], frequency_units=FREQUENCY_UNITS)

class Inductor(PassiveComponent):
    def __init__(self, value, **kwargs):
        super().__init__(value=value, units="H")

    @property
    def Z(self):
        return Impedance(num=[0, self.v * self.p], den=[1], frequency_units=FREQUENCY_UNITS)

class Capacitor(PassiveComponent):
    def __init__(self, value, **kwargs):
        super().__init__(value=value, units="F")

    @property
    def Z(self):
        return Impedance(num=[1],den=[0, self.v*self.p], frequency_units=FREQUENCY_UNITS)


