"""
Buck Converter
"""

from .smps import FixedFrequencySMPS, format_fs
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

    def __init__(self, fs, L, **kwargs) -> None:
        """
        :param fs: Switching frequency
        :param L: Primary unductance value, in Henries
        :param fs_units: optional, fs_units to use. If none, defaults to class default.
        """
        fs = format_fs(inputobj=fs, defaultunits=self._defaults["fs_units"], 
                       inputunits=kwargs.pop("fs_units", None))
        super().__init__(fs, **kwargs)

        self.L = Inductor(L)
        self.state = {"vin": None, "vout": None, "iout": None}


    