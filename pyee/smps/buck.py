"""
Buck Converter
"""

from .smps import FixedFrequencySMPS
from ..passives import Inductor

from enum import Enum

def Buck(bucktype, *args, **kwargs):
    if bucktype is BuckTypes.FixedFrequency:
        return BuckFixedFrequency(*args, **kwargs)
    else:
        raise TypeError(f"Unknown Buck converter asked for: {bucktype}")

class BuckTypes(Enum):
    FixedFrequency = 1

class BuckFixedFrequency(FixedFrequencySMPS):
    _defaults = {"fs_units": "Hz"}

    def __init__(self, fs, L, **kwargs):
        """
        :param fs: Switching frequency
        :param L: Primary unductance value, in Henries
        """
        super().__init__(fs, fs_units=kwargs.pop("fs_units", self._defaults["fs_units"]))
        self.L = Inductor(L)
        self.state = {"vin": None, "vout": None, "iout": None}


    