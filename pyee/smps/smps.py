"""
Top level classes for switched mode power supplies.
Mostly for inheritance of common items - generally not used by themselves.
"""

from abc import ABC, abstractmethod

from ..types.physicalquantity import PhysicalQuantity

class FixedFrequencySMPS(ABC, object):
    def __init__(self, fs, fs_units="Hz"):
        super().__init__()
        self._fs = PhysicalQuantity(value=fs, units=fs_units)
        self._Ts = 1/self._fs

    @property
    def fs(self):
        return self._fs

    @fs.setter
    def fs(self, val):
        self._fs.update(val)
        self._Ts.update(1/val)

    @property
    def Ts(self):
        return self._Ts

    @Ts.setter
    def Ts(self, val):
        self._Ts.update(val)
        self._fs.update(1/val)
